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

from django.conf import settings
from django.core.cache import cache
from eggplant.constants.settings import PERMISSION_DICT as PERMISSION_DICT_KEY
from eggplant.utils import import_from_string

class _Permission(object):
    _PERMISSION_DICT_PATH = getattr(settings, PERMISSION_DICT_KEY, 'eggplant.constants.defaults.PERMISSION_DICT')
    _PERMISSIONS = import_from_string(_PERMISSION_DICT_PATH)

    _REVERSE_TABLE_CACHE_KEY = 'eggplant_permissions_reverseTable'

    def __init__(self):
        self._permissions = self._PERMISSIONS

    @property
    def reverse_table(self):
        _reverse_table = cache.get(self._REVERSE_TABLE_CACHE_KEY)
        if _reverse_table is None:
            _reverse_table = dict([(v, k) for (k, v) in self._permissions.items()])
            cache.set(self._REVERSE_TABLE_CACHE_KEY, _reverse_table, 60 * 60) # Cache for 1hr
        return _reverse_table

    # Used for both str and number
    def __getitem__(self, name):
        if isinstance(name, str):
            return self._permissions[name]
        elif isinstance(name, int):
            return self.reverse_table[name]

    # Accepts both str and number
    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._permissions
        elif isinstance(item, int):
            return item in self.reverse_table
        return False

PERMISSIONS = _Permission()