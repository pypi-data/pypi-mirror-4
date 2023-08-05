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

class UserToken(object):
    def generator(self, user, unexpire=False, **kwargs):
        token = 'token_for_%s'%user
        if unexpire:
            token += '_unexpire'
        return token

    def validator(self, token, **kwargs):
        return True

    def user_from_token(self, token, **kwargs):
        return None
