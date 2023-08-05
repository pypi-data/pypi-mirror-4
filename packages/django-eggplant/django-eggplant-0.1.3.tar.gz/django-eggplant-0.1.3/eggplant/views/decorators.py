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

from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ValidationError
from django.http import QueryDict, HttpRequest
from functools import wraps
from eggplant.views.exceptions import LackOfRequiredKeyError, KeyValidationError
from eggplant.views.functions import lack_of_required_key_default_handler, key_validation_failed_default_handler
from eggplant.views import View

def _get_request_data(request):
    if request.method.lower() == 'put':
        if DJANGO_VERSION[1] >= 4:
            raw_request_data = request.body
        else:
            raw_request_data = request.raw_post_data
        requestData = QueryDict(raw_request_data)
    elif request.method.lower() == 'post':
        requestData = request.POST
    else:
        requestData = request.GET

    return requestData

def _get_wrapped_type(args):
    if isinstance(args[0], HttpRequest):
        # Function base
        viewObject = None
        request = args[0]
        is_class_based = False
    elif isinstance(args[0], View):
        # Class base
        viewObject = args[0]
        request = args[0].request
        is_class_based = True
    else:
        viewObject = None
        request = None
        is_class_based = None

    return viewObject, request, is_class_based

def required_keys(*keys, **kwargs):
    error_handler = kwargs.get('error_handler', None)
    if error_handler is None:
        error_handler = lack_of_required_key_default_handler

    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            viewObject, request, is_class_based = _get_wrapped_type(args)
            if request is None:
                return fn(*args, **kwargs)

            requestData = _get_request_data(request)

            for key in keys:
                if key not in requestData:
                    if is_class_based:
                        viewObject.response.content = ''
                        e = LackOfRequiredKeyError(key)
                        e.error_handler = viewObject.lack_of_required_key
                        raise e
                    else:
                        return error_handler(request, key, *args, **kwargs)

            return fn(*args, **kwargs)
        return wrapped

    return wrapper

def validate_keys(*key_validator_pairs, **kwargs):
    error_handler = kwargs.get('error_handler', None)
    if error_handler is None:
        error_handler = key_validation_failed_default_handler

    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            viewObject, request, is_class_based = _get_wrapped_type(args)
            if request is None:
                return fn(*args, **kwargs)

            requestData = _get_request_data(request)

            for key, validator in key_validator_pairs:
                if key in requestData:
                    try:
                        validator(requestData[key])
                    except ValidationError, e:
                        if is_class_based:
                            viewObject.response.content = ''
                            e = KeyValidationError(key, e.messages)
                            e.error_handler = viewObject.key_validation_failed
                            raise e
                        else:
                            return error_handler(request, key, *args, **kwargs)

            return fn(*args, **kwargs)
        return wrapped
    return wrapper