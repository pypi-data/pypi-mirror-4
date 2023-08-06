"""
Copyright 2012 Dian-Je Tsai, Cramdroid, and Wantoto Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, FieldError
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
import yajl as json
from eggplant.constants.defaults import EGGPLANT_MAX_PAGINATION_SIZE, EGGPLANT_DEFAULT_PAGINATION_SIZE
from eggplant.constants.settings import MAX_PAGINATION_SIZE, DEFAULT_PAGINATION_SIZE
from eggplant.utils.url import replace_querystring
from eggplant.validators.number import range_validator
from eggplant.validators.string import is_integer, is_positive_integer
from eggplant.views import exceptions
from eggplant.views.api import APIView
from eggplant.views.exceptions import ViewError
from eggplant.views.decorators import validate_keys

FILTER_CACHE_KEY_PREFIX = 'com.wantoto.eggplant.views.api.model.filter'
ORDER_CACHE_KEY_PREFIX = 'com.wantoto.eggplant.views.api.model.order'

SUPPORTED_FILTER_TYPES = [
    ('=',  '__exact'),
    ('i=', '__iexact'),
    ('>',  '__gt'),
    ('<',  '__lt'),
    ('>=', '__gte'),
    ('<=', '__lte'),
    ('%',  '__contains'),
    ('i%', '__icontains'),
    ('^',  '__startswith'),
    ('i^', '__istartswith'),
    ('$',  '__endswith'),
    ('i$', '__iendswith'),
    ('@', '__in'),
]
SUPPORTED_FILTER_TYPES_DICT = dict(SUPPORTED_FILTER_TYPES)

#-----------------------------------------------------------------------------------------------------------------------


class ModelViewBase(APIView):
    # Permission
    ACCEPT_GET = True
    ACCEPT_POST = False
    ACCEPT_PUT = False
    ACCEPT_DELETE = False

    def __init__(self, *args, **kwargs):
        super(ModelViewBase, self).__init__(*args, **kwargs)

        if not self.ACCEPT_GET and hasattr(self, 'get'):
            setattr(self, 'get', self.not_allowed_method)
        if not self.ACCEPT_POST and hasattr(self, 'post'):
            setattr(self, 'post', self.not_allowed_method)
        if not self.ACCEPT_PUT and hasattr(self, 'put'):
            setattr(self, 'put', self.not_allowed_method)
        if not self.ACCEPT_DELETE and hasattr(self, 'delete'):
            setattr(self, 'delete', self.not_allowed_method)

    def model_presenter(self, *args, **kwargs):
        return lambda x: getattr(x, 'json_dict')()

#-----------------------------------------------------------------------------------------------------------------------


class ModelCollectionView(ModelViewBase):
    MODEL_COLLECTION_CLASS = None
    ORDERABLE_FIELDS = []

    SKIP_DELIMITER_IN_FILTERS = False
    VALID_FILTERS_FOR_FIELDS = {}

    DEFAULT_PAGE_SIZE = getattr(settings, DEFAULT_PAGINATION_SIZE, EGGPLANT_DEFAULT_PAGINATION_SIZE)

    #-------------------------------------------------------------------------------------------------------------------
    # Object Lifecycle

    def __init__(self, *args, **kwargs):
        super(ModelCollectionView, self).__init__(*args, **kwargs)

        if self.MODEL_COLLECTION_CLASS is None and 'model_collection_class' in kwargs:
            self.MODEL_COLLECTION_CLASS = kwargs['model_collection_class']

    #-------------------------------------------------------------------------------------------------------------------
    # Main methods

    @validate_keys(
        (
            ('page_size', 'limit'),
            (is_positive_integer,
             range_validator(1, '>='),
             range_validator(getattr(settings, MAX_PAGINATION_SIZE, EGGPLANT_MAX_PAGINATION_SIZE), '<='))
        ),
        (('page_num', 'offset'), is_integer)
    )
    def get_collection(self, *args, **kwargs):
        # Cached one
        if hasattr(self, '_collection') and hasattr(self, '_queryset') and hasattr(self, '_meta_info'):
            return getattr(self, '_collection'), getattr(self, '_queryset'), getattr(self, '_meta_info')

        # Get query set
        query_set = self.queryset(*args, **kwargs)

        # Filter
        # "field:operation:value" with ;&| as connector
        # For example:
        #    name:=:broadcast;owner:=:sodas ==> name == broadcast AND owner == sodas
        #    name:=:broadcast&owner:=:sodas ==> name == broadcast AND owner == sodas
        #    name:=:broadcast|owner:=:sodas ==> name == broadcast OR owner == sodas
        #    name:=:broadcast;owner:=:sodas&year:=:2012 ==> name == broadcast AND (owner == sodas AND year == 2012)
        #    name:=:broadcast;owner:=:sodas|year:=:2012 ==> name == broadcast AND (owner == sodas OR year == 2012)
        #    name:=:broadcast;owner:=:sodas;year:=:2012 ==> name == broadcast AND owner == sodas AND year == 2012
        raw_filter = self.request.GET.get('filter', None)
        filters = None
        filter_cache_key = None
        if raw_filter is not None:
            # Get from cache
            filter_cache_key = '{0}.{1}'.format(FILTER_CACHE_KEY_PREFIX, raw_filter)
            filters = cache.get(filter_cache_key)
        # Make new if cache is empty
        if raw_filter is not None and filters is None:
            filters = []
            # RE: LookAhead and LookBehind (?=...) (?!...), (?<=...) (?<!...)
            # Break ";" first
            and_group = re.split(r'(?<!\\);', raw_filter) if self.SKIP_DELIMITER_IN_FILTERS else raw_filter.split(';')
            for and_pair in and_group:
                # Get components separated by '&' or '|'
                # and_pair ==> 'field:op:value&field:op:value'
                # query_components ==> ['field:op:value', '&', 'field:op:value']
                # lookups ==> ['field:op:value', 'field:op:value']
                # connectors ==> ['&']
                if self.SKIP_DELIMITER_IN_FILTERS:
                    query_components = [item.replace('\\', '') for item in re.split(r'((?<!\\)&|(?<!\\)\|)', and_pair)]
                else:
                    query_components = re.split(r'(&|\|)', and_pair)
                lookups = query_components[::2]  # a,b,c ==> a,c
                connectors = query_components[1::2]  # a,b,c ==> b

                # Create each Q objects separated by '&' or '|'
                q_objects = []
                for lookup in lookups:
                    # Component
                    try:
                        field, filter_type, value = \
                            re.split(r'(?<!\\):', lookup) if self.SKIP_DELIMITER_IN_FILTERS else lookup.split(':')
                    except ValueError:
                        raise exceptions.BadRequestError('Error filter format: {0}'.format(lookup))

                    # Field name and negate
                    negate = field.startswith('~')
                    if negate:
                        field = field[1:]

                    # Check field name and filter type
                    if not field in self.VALID_FILTERS_FOR_FIELDS:
                        continue  # Not a valid field
                    valid_filter_types = self.VALID_FILTERS_FOR_FIELDS[field]
                    if filter_type not in valid_filter_types:
                        continue  # not a valid filter type

                    # Is value a list?
                    if filter_type == '@':
                        value = re.split(r'(?<!\\),', value) if self.SKIP_DELIMITER_IN_FILTERS else value.split(',')

                    # Create object
                    q_object = self.q_object_from_filter(field, filter_type, value, negate)
                    if q_object is not None:
                        q_objects.append(q_object)

                # Connect each Q objects in a ',' via & or |
                final_q_object = None
                for index, q in enumerate(q_objects):
                    if index == 0:
                        final_q_object = q
                    else:
                        if connectors[index - 1] == '&':
                            final_q_object &= q
                        elif connectors[index - 1] == '|':
                            final_q_object |= q
                if final_q_object is not None:
                    filters.append(final_q_object)
            # Write back to cache
            cache.set(filter_cache_key, filters)
        # Apply filter to query set
        try:
            if filters is not None and len(filters) != 0:
                query_set = query_set.filter(*filters)
        except FieldError, e:
            raise ImproperlyConfigured('Field is not valid: {0}'.format(e.message))
        except ValueError:
            raise exceptions.BadRequestError('Error filter value')

        # Order
        raw_order = self.request.GET.get('order', None)
        order_cache_key = None
        orders = None
        if raw_order is not None:
            order_cache_key = '{0}.{1}'.format(ORDER_CACHE_KEY_PREFIX, raw_order)
            orders = cache.get(order_cache_key)
        if raw_order is not None and orders is None:
            order_pairs = []
            raw_orders = raw_order.split(',')
            for raw_order in raw_orders:
                if raw_order.startswith('-'):
                    order = raw_order[1:]
                    direction = -1
                else:
                    order = raw_order
                    direction = 1
                if order in self.ORDERABLE_FIELDS:
                    order_pairs.append((direction, order))
            orders = self.order_list(query_set, order_pairs, *args, **kwargs)
            cache.set(order_cache_key, orders)
        try:
            if orders is not None and len(orders) != 0:
                query_set = query_set.order_by(*orders)
        except FieldError, e:
            raise ImproperlyConfigured('Field is not valid: {0}'.format(e.message))

        meta_info = {}
        # Pagination
        default_page_size = self.DEFAULT_PAGE_SIZE
        if 'page_size' in self.request.GET or 'page_num' in self.request.GET:
            page_size = int(self.request.GET.get('page_size', default_page_size))
            current_page_num = int(self.request.GET.get('page_num', 1))

            paginator = Paginator(query_set, page_size)
            try:
                target_page = paginator.page(current_page_num)
            except EmptyPage:
                message = 'Requested page number ({0}) is out of range. (Range: {1[0]}:{1[-1]})'.format(
                    current_page_num,
                    paginator.page_range,
                )
                raise ViewError(400, message, reason='WPNOutOfPage')
            queryset = target_page.object_list

            meta_info['pagination'] = {
                'item_count': paginator.count,
                'page_count': paginator.num_pages,
                'page_size': page_size,
                'first_page': paginator.page_range[0],
                'last_page': paginator.page_range[-1],
                'current_page': current_page_num,
                'prev_page': target_page.previous_page_number() if target_page.has_previous() else None,
                'next_page': target_page.next_page_number() if target_page.has_next() else None,
            }
            if target_page.has_next():
                original_url = self.request.build_absolute_uri()
                new_url = replace_querystring(original_url, page_num=target_page.next_page_number())
                meta_info['pagination']['next_url'] = new_url
            if target_page.has_previous():
                original_url = self.request.build_absolute_uri()
                new_url = replace_querystring(original_url, page_num=target_page.previous_page_number())
                meta_info['pagination']['prev_url'] = new_url
        else:
            result_limit = int(self.request.GET.get('limit', default_page_size))
            result_offset = int(self.request.GET.get('offset', 0))

            item_count = query_set.count()
            queryset = query_set[result_offset:(result_offset + result_limit)]

            meta_info['pagination'] = {
                'item_count': item_count,
                'offset': result_offset,
                'limit': result_limit,
            }

            # Next range
            next_offset = result_offset + result_limit
            prev_offset = result_offset - result_limit
            if next_offset < item_count:
                original_url = self.request.build_absolute_uri()
                new_url = replace_querystring(original_url, offset=next_offset)
                meta_info['pagination']['next_url'] = new_url
            if prev_offset >= 0:
                original_url = self.request.build_absolute_uri()
                new_url = replace_querystring(original_url, offset=prev_offset)
                meta_info['pagination']['prev_url'] = new_url

        collection = map(self.model_presenter(*args, **kwargs), queryset)

        setattr(self, '_collection', collection)
        setattr(self, '_meta_info', meta_info)
        setattr(self, '_queryset', queryset)

        return collection, queryset, meta_info

    #-------------------------------------------------------------------------------------------------------------------
    # HTTP method

    def get(self, *args, **kwargs):
        collection, queryset, meta_info = self.get_collection(*args, **kwargs)
        if self.show_meta_in_response(*args, **kwargs):
            result = {
                'data': collection,
                'meta': meta_info,
            }
        else:
            result = collection
            self.response['X-Meta'] = json.dumps(meta_info)

        self.response.content = json.dumps(result)

    def post(self, *args, **kwargs):
        new_model = self.create_model(self.MODEL_COLLECTION_CLASS, *args, **kwargs)
        if new_model is None:
            raise NotImplementedError('create_model method doesn\'t return a new model object.')

        model_presentation = self.model_presenter(*args, **kwargs)(new_model)
        self.response.content = json.dumps(model_presentation)

    def delete(self, *args, **kwargs):
        self.get(*args, **kwargs)
        collection, queryset, meta_info = self.get_collection(*args, **kwargs)

        id_to_delete = [item['id'] for item in queryset.values('id')]
        items_to_delete = self.MODEL_COLLECTION_CLASS.objects.filter(id__in=id_to_delete)
        items_to_delete.delete()

    #-------------------------------------------------------------------------------------------------------------------
    # Public Method

    def show_meta_in_response(self, *args, **kwargs):
        return False

    def create_model(self, ModelClass, *args, **kwargs):
        return None

    def queryset(self, *args, **kwargs):
        ModelClass = self.MODEL_COLLECTION_CLASS
        if ModelClass is None:
            raise ImproperlyConfigured('Forget to set MODEL_CLASS for this ModelCollectionView')
        return ModelClass.objects.all()

    def order_list(self, query_set, orders, *args, **kwargs):
        result_order_list = []
        for direction, raw_field in orders:
            order = self.field_for_order(raw_field, direction)
            if order is None:
                continue
            if isinstance(order, (list, tuple)):
                result_order_list += order
            else:
                result_order_list.append(order)
        return  result_order_list

    def q_object_from_filter(self, field, filter_type, value, negate):
        arguments = {(field + SUPPORTED_FILTER_TYPES_DICT[filter_type]): value}
        q = Q(**arguments)
        return ~q if negate else q

    def field_for_order(self, order, direction, *args, **kwargs):
        return order if direction == 1 else '-' + order

    def model_presenter(self, *args, **kwargs):
        return lambda x: getattr(x, 'json_dict')(summary=True)

#-----------------------------------------------------------------------------------------------------------------------


class ModelView(ModelViewBase):
    # Model
    MODEL_CLASS = None
    MODEL_NAME = None

    #-------------------------------------------------------------------------------------------------------------------
    # Object Lifecycle

    def __init__(self, *args, **kwargs):
        super(ModelView, self).__init__(*args, **kwargs)

        if self.MODEL_CLASS is None and 'model_class' in kwargs:
            self.MODEL_CLASS = kwargs['model_class']
        if self.MODEL_NAME is None:
            if 'model_name' in kwargs:
                self.MODEL_NAME = kwargs['model_name']
            else:
                self.MODEL_NAME = self.MODEL_CLASS.__name__

    #-------------------------------------------------------------------------------------------------------------------
    # HTTP Methods

    def get(self, *args, **kwargs):
        model_object = self.model_object(*args, **kwargs)
        model_presentation = self.model_presenter(*args, **kwargs)(model_object)

        self.response.content = json.dumps(model_presentation)

    def put(self, *args, **kwargs):
        model_object = self.model_object(*args, **kwargs)

        new_model_object = self.update_model_object(model_object, *args, **kwargs)
        if new_model_object is not None:
            # Set cached one to updated one.
            self._model = new_model_object
        else:
            # Remove cached, let it update later
            delattr(self, '_model')

        self.get(*args, **kwargs)  # response content

    def delete(self, *args, **kwargs):
        model_object = self.model_object(*args, **kwargs)
        self.get(*args, **kwargs)  # response content
        model_object.delete()

    #-------------------------------------------------------------------------------------------------------------------
    # Public Methods

    def model_object(self, *args, **kwargs):
        # kwargs must contains "model_id" (from url)
        if hasattr(self, '_model'):
            return self._model

        ModelClass = kwargs['model_class'] if 'model_class' in kwargs else self.MODEL_CLASS
        if ModelClass is None:
            raise ImproperlyConfigured('Forget to set MODEL_CLASS for this ModelView')

        try:
            model_object = self.get_model(ModelClass, *args, **kwargs)
        except ModelClass.DoesNotExist:
            raise exceptions.ModelDoesNotExistError(self.MODEL_NAME)

        self._model = model_object
        setattr(self, self.MODEL_NAME.lower(), model_object)
        return model_object

    def update_model_object(self, original_model_object, *args, **kwargs):
        """For performance reason, it's good to return updated model object"""
        return original_model_object

    def get_model(self, ModelClass, model_id, *args, **kwargs):
        return ModelClass.objects.get(id=model_id)
