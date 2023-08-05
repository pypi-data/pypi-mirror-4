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

from functools import wraps
import types
from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ValidationError
from django.http import QueryDict, HttpRequest
import six
from eggplant.views.exceptions import LackOfRequiredKeyError, KeyValidationError
from eggplant.views.functions import lack_of_required_key_default_handler, key_validation_failed_default_handler
from eggplant.views import View

def _get_request_data(request):
    if request.method.lower() == 'put':
        if DJANGO_VERSION[1] >= 4:
            raw_request_data = request.body
        else:
            raw_request_data = request.raw_post_data
        request_data = QueryDict(raw_request_data)
    elif request.method.lower() == 'post':
        request_data = request.POST
    else:
        request_data = request.GET

    return request_data


def _get_wrapped_type(args):
    if isinstance(args[0], HttpRequest):
        # Function base
        view_object = None
        request = args[0]
        is_class_based = False
    elif isinstance(args[0], View):
        # Class base
        view_object = args[0]
        request = args[0].request
        is_class_based = True
    else:
        view_object = None
        request = None
        is_class_based = None

    return view_object, request, is_class_based


def required_keys(*keys, **kwargs):
    error_handler = kwargs.get('error_handler', None)
    if error_handler is None:
        error_handler = lack_of_required_key_default_handler

    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            view_object, request, is_class_based = _get_wrapped_type(args)
            if request is None:
                return fn(*args, **kwargs)

            request_data = _get_request_data(request)

            for key in keys:
                if key not in request_data:
                    if is_class_based:
                        view_object.response.content = ''
                        e = LackOfRequiredKeyError(key)
                        e.error_handler = view_object.lack_of_required_key
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
            view_object, request, is_class_based = _get_wrapped_type(args)
            if request is None:
                return fn(*args, **kwargs)

            request_data = _get_request_data(request)

            # Check what's input
            kv_pairs = key_validator_pairs
            if len(key_validator_pairs)==2:
                if isinstance(key_validator_pairs[0], (list, tuple, six.string_types)) and\
                   (isinstance(key_validator_pairs[1], (list, tuple, types.FunctionType, staticmethod)) or
                    hasattr(key_validator_pairs[1], '__call__')):
                    kv_pairs = [(key_validator_pairs[0], key_validator_pairs[1])]

            for request_key, validator_set in kv_pairs:
                if not isinstance(request_key, (list, tuple)): keys = [request_key]
                else: keys = request_key

                if not isinstance(validator_set, (list, tuple)): validators = [validator_set]
                else: validators = validator_set

                for key in keys:
                    for validator in validators:
                        if key in request_data:
                            try:
                                if is_class_based:
                                    if isinstance(validator, staticmethod):
                                        validator_name = validator.__func__.__name__
                                        arguments = (request_data[key],)
                                    else:
                                        # ==> isinstance(validator, types.FunctionType)
                                        validator_name = validator.__name__
                                        arguments = (view_object, request_data[key])

                                    if hasattr(view_object, validator_name):
                                        getattr(view_object.__class__, validator_name)(*arguments)
                                    else:
                                        validator(request_data[key])
                                else:
                                    validator(request_data[key])
                            except ValidationError, e:
                                if is_class_based:
                                    view_object.response.content = ''
                                    e = KeyValidationError(key, e.messages)
                                    e.error_handler = view_object.key_validation_failed
                                    raise e
                                else:
                                    return error_handler(request, key, *args, **kwargs)

            return fn(*args, **kwargs)

        return wrapped

    return wrapper
