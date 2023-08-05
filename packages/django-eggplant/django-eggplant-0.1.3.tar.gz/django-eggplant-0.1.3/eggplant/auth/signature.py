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

from eggplant.models import AccessKey

def generate_api_secret(app_id):
    return 'api_secret_for_%s'%app_id

class SignatureKey(object):
    @staticmethod
    def get_access_key(app_id):
        try:
            return AccessKey.objects.get(app_id=app_id)
        except AccessKey.DoesNotExist:
            return None # Who are you?

    @classmethod
    def generator(cls, app_id, path):
        return 'signature_for_%s_at_%s'%(app_id, path)

    @classmethod
    def validator(cls, path, key):
        return True