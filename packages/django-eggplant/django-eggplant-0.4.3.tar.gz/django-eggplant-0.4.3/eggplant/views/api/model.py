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

import json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, EmptyPage
from eggplant.validators.number import range_validator
from eggplant.validators.string import is_positive_integer
from eggplant.views import exceptions
from eggplant.views.api import APIView
from eggplant.views.exceptions import ViewError
from eggplant.views.decorators import validate_keys
from eggplant.constants.settings import MAX_PAGINATION_SIZE, DEFAULT_PAGINATION_SIZE
from eggplant.constants import defaults as eggplant_defaults

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
    DEFAULT_PAGE_SIZE = getattr(settings, DEFAULT_PAGINATION_SIZE, eggplant_defaults.EGGPLANT_DEFAULT_PAGINATION_SIZE)

    #-------------------------------------------------------------------------------------------------------------------
    # Object Lifecycle

    def __init__(self, *args, **kwargs):
        super(ModelCollectionView, self).__init__(*args, **kwargs)

        if self.MODEL_COLLECTION_CLASS is None and kwargs.has_key('model_collection_class'):
            self.MODEL_COLLECTION_CLASS = kwargs['model_collection_class']

    #-------------------------------------------------------------------------------------------------------------------
    # Main methods

    @validate_keys(
        (('page_size', 'limit'),
          (is_positive_integer, range_validator(1, '>='),
           range_validator(getattr(settings, MAX_PAGINATION_SIZE, eggplant_defaults.EGGPLANT_MAX_PAGINATION_SIZE), '<=')
          )
         ),
        (('page_num', 'offset'), is_positive_integer)
    )
    def get_collection(self, *args, **kwargs):
        # Cached one
        if hasattr(self, '_collection') and hasattr(self, '_queryset') and hasattr(self, '_meta_info'):
            return getattr(self, '_collection'), getattr(self, '_queryset'), getattr(self, '_meta_info')

        # Get query set
        query_set = self.queryset(*args, **kwargs)

        # TODO: Add Order and Filter

        meta_info = {}
        # Pagination
        default_page_size = self.DEFAULT_PAGE_SIZE
        if self.request.GET.has_key('page_size') or self.request.GET.has_key('page_num'):
            page_size = int(self.request.GET.get('page_size', default_page_size))
            current_page_num = int(self.request.GET.get('page_num', 1))

            paginator = Paginator(query_set, page_size)
            try:
                target_page = paginator.page(current_page_num)
            except EmptyPage:
                raise ViewError(400, 'Requested page number (%s) is out of range. (Range: %s:%s)'%(
                    current_page_num,
                    paginator.page_range[0],
                    paginator.page_range[-1],
                    ),
                    reason='WPNOutOfPage'
                )
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
        else:
            result_limit = int(self.request.GET.get('limit', default_page_size))
            result_offset = int(self.request.GET.get('offset', 0))

            item_count = query_set.count()
            queryset = query_set[result_offset:result_offset+result_limit]

            meta_info['pagination'] = {
                'item_count': item_count,
                'offset': result_offset,
                'limit': result_limit,
            }

        collection = map(self.model_presenter(*args, **kwargs), queryset)

        setattr(self, '_collection', collection)
        setattr(self, '_meta_info', meta_info)
        setattr(self, '_queryset', queryset)

        return collection, queryset, meta_info

    #-------------------------------------------------------------------------------------------------------------------
    # HTTP method

    def get(self, *args, **kwargs):
        collection, queryset, meta_info = self.get_collection(*args, **kwargs)

        result = {
            'data': collection,
            'meta': meta_info,
        }
        self.response.content = json.dumps(result)

    def post(self, *args, **kwargs):
        new_model = self.create_model(self.MODEL_COLLECTION_CLASS, *args, **kwargs)
        if new_model is None:
            raise NotImplementedError, 'create_model method doesn\'t return a new model object.'

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

    def create_model(self, ModelClass, *args, **kwargs):
        return None

    def queryset(self, *args, **kwargs):
        ModelClass = self.MODEL_COLLECTION_CLASS
        if ModelClass is None:
            raise ImproperlyConfigured, 'Forget to set MODEL_CLASS for this ModelCollectionView'
        return ModelClass.objects.all()

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

        if self.MODEL_CLASS is None and kwargs.has_key('model_class'):
            self.MODEL_CLASS = kwargs['model_class']
        if self.MODEL_NAME is None:
            if kwargs.has_key('model_name'):
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

        self.get(*args, **kwargs) # response content

    def delete(self, *args, **kwargs):
        model_object = self.model_object(*args, **kwargs)
        self.get(*args, **kwargs) # response content
        model_object.delete()

    #-------------------------------------------------------------------------------------------------------------------
    # Public Methods

    def model_object(self, *args, **kwargs):
        # kwargs must contains "model_id" (from url)
        if hasattr(self, '_model'): return self._model

        ModelClass = kwargs['model_class'] if 'model_class' in kwargs else self.MODEL_CLASS
        if ModelClass is None:
            raise ImproperlyConfigured, 'Forget to set MODEL_CLASS for this ModelView'

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
