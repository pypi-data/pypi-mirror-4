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

import six
if six.PY3:
    import http.client as httplib
else:
    import httplib

class ViewError(Exception):
    def __init__(self, status_code, message=None):
        self.status_code = status_code
        self.reason = httplib.responses[status_code]
        self.message = message or 'Something goes wrong ...'
        self.error_handler = None
        self.user_info = None

#-----------------------------------------------------------------------------------------------------------------------
# 400 Bad Request
# Request syntax error (Lack of required keys, invalid value of arguments)

class BadRequestError(ViewError):
    def __init__(self, message=None):
        super(BadRequestError, self).__init__(httplib.BAD_REQUEST, message or 'Bad Request')

class LackOfRequiredKeyError(BadRequestError):
    def __init__(self, key):
        super(LackOfRequiredKeyError, self).__init__('Key "%s" is required.'%key)
        self.user_info = {'key': key}

class KeyValidationError(BadRequestError):
    def __init__(self, key, messages):
        message = ('Key "%s" is invalid.' % key + ' ' + ' '.join(messages)).strip()
        super(KeyValidationError, self).__init__(message)
        self.user_info = {
            'key': key,
            'raw_messages': messages
        }

#-----------------------------------------------------------------------------------------------------------------------
# 401 Unauthorized
# Failed to authenticate user. Credential error or lack of required credential

class UnauthorizedError(ViewError):
    def __init__(self, message=None):
        super(UnauthorizedError, self).__init__(httplib.UNAUTHORIZED,
            message or 'You have to login before access this resources.')

class SignatureKeyInvalidError(UnauthorizedError):
    def __init__(self):
        super(SignatureKeyInvalidError, self).__init__('The signature key is invalid.')

class UserIdentityUnknownError(UnauthorizedError):
    def __init__(self):
        super(UserIdentityUnknownError, self).__init__('Your identity is unknown.')

#-----------------------------------------------------------------------------------------------------------------------
# 403 Forbidden
# Authenticated but don't have enough permission

class ForbiddenError(ViewError):
    def __init__(self, message=None):
        super(ForbiddenError, self).__init__(httplib.FORBIDDEN,
            message or 'You have no permission to access this resources.')

class InvalidHttpRefererError(ForbiddenError):
    def __init__(self):
        super(InvalidHttpRefererError, self).__init__('This http refer of this request is not accepted.')

class AppHaveNoPermissionError(ForbiddenError):
    def __init__(self):
        super(AppHaveNoPermissionError, self).__init__('This application doesn\'t have permission to access this.')

class UserHaveNoPermissionError(ForbiddenError):
    def __init__(self):
        super(UserHaveNoPermissionError, self).__init__('You have no permission to access this.')

#-----------------------------------------------------------------------------------------------------------------------
# 404 Not Found

class NotFoundError(ViewError):
    def __init__(self, message=None):
        super(NotFoundError, self).__init__(httplib.NOT_FOUND, message or 'Item not found')

class ModelDoesNotExistError(NotFoundError):
    def __init__(self, model_name):
        super(ModelDoesNotExistError, self).__init__('No such %s item.'%model_name)

#-----------------------------------------------------------------------------------------------------------------------
# 405 Method Not Allowed

class MethodNotAllowedError(ViewError):
    def __init__(self, http_request, message=None):
        super(MethodNotAllowedError, self).__init__(httplib.METHOD_NOT_ALLOWED,
            message or 'HTTP %s Method is not allowed.'%http_request.method.upper())

#-----------------------------------------------------------------------------------------------------------------------
# 409 Conflict

class ConflictError(ViewError):
    def __init__(self, message=None):
        super(ConflictError, self).__init__(httplib.CONFLICT, message or 'Conflict')

class DuplicatedInsertionError(ConflictError):
    def __init__(self, message=None):
        super(DuplicatedInsertionError, self).__init__(
            message or 'Requested insertion contains duplicated value for unique keys.')
