"""
Copyright 2012 Dian-Je Tsai and Wantoto Inc

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
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage
from eggplant.validators.string import is_positive_integer
from eggplant.views import APIView
from eggplant.views.exceptions import ViewError
from eggplant.views.decorators import validate_keys
from eggplant.constants.settings import MAX_PAGINATION_SIZE, DEFAULT_PAGINATION_SIZE
from eggplant.constants import defaults as eggplant_defaults

class ModelCollectionAPIView(APIView):
    MODEL_CLASS = None
    DEFAULT_PAGE_SIZE = getattr(settings, DEFAULT_PAGINATION_SIZE, eggplant_defaults.EGGPLANT_DEFAULT_PAGINATION_SIZE)

    @staticmethod
    def result_length_validator(length):
        length = int(length)
        max_page_size = getattr(settings, MAX_PAGINATION_SIZE, eggplant_defaults.EGGPLANT_MAX_PAGINATION_SIZE)
        if length < 1 or length > max_page_size:
            raise ValidationError('It should be between 1 and %s.'%max_page_size)

    @validate_keys(
        (('page_size', 'limit'), (is_positive_integer, result_length_validator)),
        (('page_num', 'offset'), is_positive_integer)
    )
    def get(self, *args, **kwargs):
        # Get query set
        query_set = self.query_set(*args, **kwargs)

        # TODO: Add Order and Filter

        result = {}
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
                    )
                )
            raw_collection = target_page.object_list

            result['pagination'] = {
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
            raw_collection = query_set[result_offset:result_offset+result_limit]

            result['pagination'] = {
                'item_count': item_count,
                'offset': result_offset,
                'limit': result_limit,
                }

        collection = map(self.model_presenter(*args, **kwargs), raw_collection)

        result['data'] = collection
        self.response.content = json.dumps(result)

    def model_presenter(self, *args, **kwargs):
        return lambda x: getattr(x, 'json_dict')()

    def query_set(self, *args, **kwargs):
        ModelClass = self.MODEL_CLASS
        return ModelClass.objects.all()
