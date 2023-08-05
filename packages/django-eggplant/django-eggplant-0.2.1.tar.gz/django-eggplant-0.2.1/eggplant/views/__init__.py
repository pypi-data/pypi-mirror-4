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
from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.utils.decorators import classonlymethod
from eggplant.constants import HTTP_METHOD
from eggplant.constants.settings import HTTPS_ONLY, SIGNATURE_KEY_CLASS, DEPLOYED, AJAX_SIGNATURE_KEY_CLASS
from eggplant.utils import import_from_string
from eggplant.views import exceptions
from eggplant.views.exceptions import ViewError

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
                raise ViewError(400, 'This url accepts HTTPS only.')

            # Check allowed http methods
            if request.method.upper() in HTTP_METHOD and \
               hasattr(self, request.method.lower()):
                handler = getattr(self, request.method.lower())
            else:
                raise ViewError(405, 'HTTP %s Method is not allowed.'%self.request.method.upper())

            # Extend django request query dict
            if request.method.upper() == 'PUT':
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

class APIView(View):
    AUTH_METHODS = ('None', 'Session', 'Token')

    def only_accept_https(self, *args, **kwargs):
        return getattr(settings, DEPLOYED, True)

    def should_check_signature_key(self, *args, **kwargs):
        return True

    def user_authentication_method(self, *args, **kwargs):
        if self.request.is_ajax():
            return APIView.AUTH_METHODS[1]
        else:
            return APIView.AUTH_METHODS[2]

    def signature_key(self, *args, **kwargs):
        return self.request.META.get('HTTP_X_REQUEST_SIGNATURE', None)

    def signature_key_class(self, *args, **kwargs):
        key_class_path = getattr(settings, SIGNATURE_KEY_CLASS, None)
        if self.request.is_ajax():
            key_class_path = getattr(settings, AJAX_SIGNATURE_KEY_CLASS, key_class_path)

        if key_class_path is not None:
            SignatureKey = import_from_string(key_class_path)
        else:
            from eggplant.auth.signature import SignatureKeyBase as SignatureKey
        return SignatureKey

    def user_token(self, *args, **kwargs):
        if self.request.is_ajax():
            return getattr(self.request, self.request.method.upper()).get('token', None)
        else:
            return self.request.META.get('HTTP_X_USER_TOKEN', None)

    def required_permissions(self, *args, **kwargs):
        return None

    def authenticate(self, *args, **kwargs):
        # Check app identification
        if self.should_check_signature_key(*args, **kwargs):
            SignatureKey = self.signature_key_class(*args, **kwargs)
            signature_key_handler = SignatureKey()

            key = self.signature_key(*args, **kwargs)
            key_is_valid = signature_key_handler.validator(self.request.path, key)
            if not key_is_valid:
                raise exceptions.SignatureKeyInvalidError()

            # Check permission
            required_permissions = self.required_permissions(*args, **kwargs)
            if required_permissions is not None:
                if not signature_key_handler.have_permission(key, required_permissions):
                    raise exceptions.AppHaveNoPermissionError()

        # Check user identification
        user_auth_method = self.user_authentication_method(*args, **kwargs)
        if user_auth_method=='Session':
            if not self.request.user.is_authenticated():
                raise exceptions.UserIdentityUnknownError()
        elif user_auth_method=='Token':
            token = self.user_token(*args, **kwargs)
            user = authenticate(token=token)
            if user is None:
                raise exceptions.UserIdentityUnknownError()
            else:
                login(self.request, user)

class HTMLView(View):
    def __init__(self, *args, **kwargs):
        super(HTMLView, self).__init__(*args, **kwargs)
        self.html_filename = kwargs.get('html_filename', None)

    def get(self, *args, **kwargs):
        if self.html_filename is not None:
            context = {}
            context.update(self.init_kwargs)
            context.update(kwargs)
            context.update(self.request.GET)
            self.response = render(self.request, self.html_filename, context)
        else:
            self.response.write('No assigned html template')