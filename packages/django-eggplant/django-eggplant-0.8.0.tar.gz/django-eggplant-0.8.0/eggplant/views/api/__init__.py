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

import yajl as json
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from ground_soil.lang import import_from_string
from eggplant.constants.settings import DEPLOYED, SIGNATURE_KEY_CLASS, AJAX_SIGNATURE_KEY_CLASS, DEFAULT_AUTH_METHOD
from eggplant.datatype import AttributedDict
from eggplant.views import View, exceptions


class APIView(View):
    AUTH_METHODS = AttributedDict({'NoAuth': 0, 'Session': 1, 'Token': 2})

    @csrf_exempt
    def handle(self, request, *args, **kwargs):
        return super(APIView, self).handle(request, *args, **kwargs)

    def only_accept_https(self, *args, **kwargs):
        return getattr(settings, DEPLOYED, True)

    def should_check_signature_key(self, *args, **kwargs):
        return True

    def user_authentication_method(self, *args, **kwargs):
        default_auth_method = getattr(settings, DEFAULT_AUTH_METHOD, None)
        if default_auth_method is not None:
            return default_auth_method

        if 'auth_method' in self.init_kwargs:
            return self.init_kwargs['auth_method']

        if self.request.is_ajax():
            return APIView.AUTH_METHODS.Session
        else:
            return APIView.AUTH_METHODS.Token

    def signature_key(self, *args, **kwargs):
        return self.request.META.get('HTTP_X_REQUEST_SIGNATURE', '')

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
            self.signature_key_handler = SignatureKey()

            key = self.signature_key(*args, **kwargs)
            key_is_valid = self.signature_key_handler.validator(self.request.path, key)
            if not key_is_valid:
                raise exceptions.SignatureKeyInvalidError()

            # Check permission
            required_permissions = self.required_permissions(*args, **kwargs)
            if required_permissions is not None:
                if not self.signature_key_handler.have_permission(key, required_permissions):
                    raise exceptions.AppHaveNoPermissionError()

        # Check user identification
        user_auth_method = self.user_authentication_method(*args, **kwargs)
        should_check_user_permission = True
        if user_auth_method == self.AUTH_METHODS.Session:
            if not self.request.user.is_authenticated():
                raise exceptions.UserIdentityUnknownError()
        elif user_auth_method == self.AUTH_METHODS.Token:
            token = self.user_token(*args, **kwargs)
            user = authenticate(token=token)
            if user is None:
                raise exceptions.UserIdentityUnknownError()
            else:
                login(self.request, user)
        else:
            should_check_user_permission = False

        # Check user's permission
        if should_check_user_permission:
            request_method = self.request.method.lower()
            if (request_method == 'get' and not self.user_can_read(*args, **kwargs)) or\
               (request_method == 'post' and not self.user_can_create(*args, **kwargs)) or\
               (request_method == 'put' and not self.user_can_update(*args, **kwargs)) or\
               (request_method == 'delete' and not self.user_can_delete(*args, **kwargs)):
                raise exceptions.UserHaveNoPermissionError()

    def user_can_read(self, *args, **kwargs):
        return True

    def user_can_create(self, *args, **kwargs):
        return False

    def user_can_update(self, *args, **kwargs):
        return False

    def user_can_delete(self, *args, **kwargs):
        return False

    def default_error_handler(self, error_obj):
        self.response['Content-Type'] = 'application/json'
        result = {
            'http_status_reason': error_obj.reason,
            'http_status_code': error_obj.status_code,
            'error': error_obj.message,
        }
        meta = {}
        if error_obj.user_info and len(error_obj.user_info.items()):
            meta['user_info'] = error_obj.user_info
        if error_obj.init_kwargs and len(error_obj.init_kwargs.items()):
            meta['keyword'] = error_obj.init_kwargs

        if len(meta.items()):
            try:
                result['meta'] = json.loads(json.dumps(meta))
            except TypeError:
                pass
        self.response.content = json.dumps(result)

    def post_handle(self, *args, **kwargs):
        self.response['Content-Type'] = 'application/json'


class DevAPIView(APIView):
    def only_accept_https(self, *args, **kwargs):
        return False

    def should_check_signature_key(self, *args, **kwargs):
        return False

    def user_authentication_method(self, *args, **kwargs):
        return APIView.AUTH_METHODS.NoAuth
