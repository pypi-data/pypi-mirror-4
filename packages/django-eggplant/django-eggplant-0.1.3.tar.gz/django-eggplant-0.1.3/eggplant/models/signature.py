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

from django.db import models
from eggplant import APP_LABEL
from eggplant.auth.permissions import PERMISSIONS as permission_list

class AccessKey(models.Model):
    app_id = models.CharField(max_length=64, unique=True, db_index=True)
    api_secret = models.CharField(max_length=512)
    # A 64 bit integer. We can have 64 different permissions.
    permissions = models.BigIntegerField(default=0b0)

    class Meta:
        app_label = APP_LABEL

    def _merge_permission(self, permissions):
        permission_collection = 0
        for permission in permissions:
            if permission not in permission_list:
                raise ValueError, 'No such permission: %s' % permission
                # We save only number format
            if isinstance(permission, str):
                permission = getattr(permission_list, permission)
            permission_collection |= permission
        return permission_collection

    def set_permission(self, permissions):
        if isinstance(permissions, (list, tuple)):
            permission = self._merge_permission(permissions)
        else:
            permission = permissions
        self.permissions |= permission

    def remove_permission(self, permissions):
        if isinstance(permissions, (list, tuple)):
            permission = self._merge_permission(permissions)
        else:
            permission = permissions
        self.permissions &= ~permission

    def permission_bin_str(self):
        return bin(self.permissions)

    def permission_set(self):
        result = []
        position = 0 # 2 power series
        for perm in bin(self.permissions)[2:][::-1]:
            if perm=='1': # Yeah, it has this.
                permValue = pow(2, position) # Which number are you?
                result += [permission_list[permValue]] # Get name and save
            position += 1
        return set(result)
