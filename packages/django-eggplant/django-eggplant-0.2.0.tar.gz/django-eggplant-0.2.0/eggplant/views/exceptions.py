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

class ViewError(Exception):
    def __init__(self, status_code, message=None):
        if message is None: message = 'Something goes wrong ...'
        self.status_code = status_code
        self.message = message
        self.error_handler = None

class LackOfRequiredKeyError(ViewError):
    def __init__(self, key):
        status_code = 400
        message = 'Key "%s" is required.'%key
        super(LackOfRequiredKeyError, self).__init__(status_code, message)
        self.key = key

class KeyValidationError(ViewError):
    def __init__(self, key, messages):
        status_code = 400
        message = 'Key "%s" is invalid.' % key
        super(KeyValidationError, self).__init__(status_code, message)
        self.key = key
        self.raw_messages = messages

class AuthenticationFailedError(ViewError):
    def __init__(self, message=None):
        status_code = 401
        if message is None:
            message = 'You have to login before access this resources.'
        super(AuthenticationFailedError, self).__init__(status_code, message)

class SignatureKeyInvalidError(AuthenticationFailedError):
    def __init__(self):
        super(SignatureKeyInvalidError, self).__init__(message='The signature key is invalid.')

class NoPermissionError(ViewError):
    def __init__(self, message=None):
        status_code = 403
        if message is None:
            message = 'You have no permission to access this resources.'
        super(NoPermissionError, self).__init__(status_code, message)

class InvalidHttpRefererError(NoPermissionError):
    def __init__(self):
        super(InvalidHttpRefererError, self).__init__('This http refer of this request is not accepted.')

class AppHaveNoPermissionError(NoPermissionError):
    def __init__(self):
        super(AppHaveNoPermissionError, self).__init__('This application doesn\'t have permission to access this.')

class UserIdentityUnknownError(NoPermissionError):
    def __init__(self):
        super(UserIdentityUnknownError, self).__init__('Your identity is unknown.')
