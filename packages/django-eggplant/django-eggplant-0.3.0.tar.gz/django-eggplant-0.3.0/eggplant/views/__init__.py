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

from functools import update_wrapper
import httplib
from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.http import HttpResponse, QueryDict
from django.utils.decorators import classonlymethod
from eggplant.constants import HTTP_METHOD
from eggplant.constants.settings import HTTPS_ONLY
from eggplant.views.exceptions import ViewError, MethodNotAllowedError

class View(object):
    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs

    @classonlymethod
    def view(cls, *init_args, **init_kwargs):
        def view(request, *args, **kwargs):
            self = cls(*init_args, **init_kwargs)

            # Automatically add 'head' method
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                def _head(self, *args, **kwargs):
                    getattr(self, 'get')(*args, **kwargs)
                    self.response.content = ''
                setattr(self, 'head', _head)

            return self.handle(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.handle, assigned=())
        return view

    def handle(self, request, *args, **kwargs):
        self.request = request
        self.response = HttpResponse()

        # Go
        try:
            # HTTPS?
            if self.only_accept_https(*args, **kwargs) and not self.request.is_secure():
                raise ViewError(httplib.BAD_REQUEST, 'This url accepts HTTPS only.')

            # Check allowed http methods
            if request.method.upper() in HTTP_METHOD and \
               hasattr(self, request.method.lower()):
                handler = getattr(self, request.method.lower())
            else:
                raise MethodNotAllowedError(request)

            # Extend django request query dict
            if request.method.upper() == 'PUT':
                if not hasattr(request, 'PUT'):
                    if DJANGO_VERSION[1] >= 4:
                        raw_body = self.request.body
                    else:
                        raw_body = self.request.raw_post_data
                    setattr(self.request, request.method.upper(), QueryDict(raw_body))
            elif request.method.upper() not in ('POST', 'GET'):
                setattr(self.request, request.method.upper(), self.request.GET)

            # Check HTTP Refer
            http_referer = self.request.META.get('HTTP_REFERER', None)
            self.check_http_referer(http_referer, *args, **kwargs)

            # Authenticate
            self.authenticate(*args, **kwargs)

            # Dispatch
            handler(*args, **kwargs)

        # Handler
        except ViewError, e:
            self.response.content = ''
            self.response.status_code = e.status_code

            if e.error_handler is not None:
                error_handler = e.error_handler
            else:
                error_handler = self.default_error_handler
            error_handler(e)

        return self.response

    # Extend query dict
    @property
    def PUT(self):
        if not hasattr(self, '_put'):
            if self.request.method.lower()=='put':
                if DJANGO_VERSION[1] >= 4:
                    raw_body = self.request.body
                else:
                    raw_body = self.request.raw_post_data
                self._put = QueryDict(raw_body)
            else:
                self._put = QueryDict({})

        return self._put

    def only_accept_https(self, *args, **kwargs):
        return getattr(settings, HTTPS_ONLY, False)

    def authenticate(self, *args, **kwargs):
        pass

    def check_http_referer(self, referer, *args, **kwargs):
        #raise exceptions.InvalidHttpRefererError
        pass

    def failed_to_authenticate_handler(self, error_obj):
        self.response['Content-Type'] = 'text/plain'
        self.response.content = error_obj.message

    def default_error_handler(self, error_obj):
        self.response['Content-Type'] = 'text/plain'
        self.response.content = error_obj.message

    def lack_of_required_key(self, error_obj):
        self.default_error_handler(error_obj)

    def key_validation_failed(self, error_obj):
        self.default_error_handler(error_obj)

    def not_allowed_method(self, *args, **kwargs):
        raise MethodNotAllowedError(self.request)
