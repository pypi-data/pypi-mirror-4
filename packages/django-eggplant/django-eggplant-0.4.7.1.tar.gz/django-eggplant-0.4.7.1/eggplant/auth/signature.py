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

class SignatureKeyBase(object):
    def validator(self, path, key, **kwargs):
        # Override this
        return True

    def generator(self, *args, **kwargs):
        return ''

    def have_permission(self, key, required_permission):
        return True

class SignatureKey(SignatureKeyBase):
    ###################
    ## Must override ##
    ###################

    def generator(self, app_id, path, **kwargs):
        # Override this
        return 'signature_for_%s_at_%s' % (app_id, path)

    def app_id_from_key(self, key):
        # Override this
        return ''

    #######################
    ## Optional override ##
    #######################

    def get_access_key(self, app_id):
        try:
            return AccessKey.objects.get(app_id=app_id)
        except AccessKey.DoesNotExist:
            return None # Who are you?

    def have_permission(self, key, required_permission):
        access_key = self.get_access_key(self.app_id_from_key(key))
        return access_key.have_permission(required_permission)

class AjaxSignatureKey(SignatureKeyBase):
    def generator(self, request, **kwargs):
        # Override this
        return 'ajax_signature_for_%s'%request.path