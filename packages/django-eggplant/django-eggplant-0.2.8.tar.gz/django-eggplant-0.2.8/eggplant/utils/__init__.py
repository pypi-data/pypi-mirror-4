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

import imp
import os
import types
import urllib
import urlparse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

def valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def append_query_string_to_URL(url, data):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))

    if isinstance(data, str):
        data = dict(urlparse.parse_qsl(data))
    query.update(data)

    url_parts[4] = urllib.urlencode(query)

    return urlparse.urlunparse(url_parts)

def sql_string_from_query_set(qs, *args):
    sql = str(qs.query)
    for target, newString in args:
        sql = sql.replace(target, newString)
    return sql

def import_from_string(path):
    path_components = path.split('.')
    class_name = path_components[-1]
    package = '.'.join(path_components[:-1])
    return getattr(__import__(package, fromlist=[class_name]), class_name)

def dict_from_module(module_object, key_filter=None):
    if key_filter is None: key_filter = lambda x: True

    result = {}
    for attribute in dir(module_object):
        if key_filter(attribute):
            result[attribute] = getattr(module_object, attribute)
    return result


class SettingsDict(object):
    def __init__(self, default_settings, user_settings, **patches):
        if isinstance(default_settings, (str, unicode)):
            default_settings_name = os.path.split(os.path.splitext(default_settings)[0])[-1]
            default_settings = imp.load_source(default_settings_name, default_settings)
        if isinstance(default_settings, types.ModuleType):
            default_settings = dict_from_module(default_settings, lambda key: key.isupper())

        if isinstance(user_settings, (str, unicode)):
            user_settings_name = os.path.split(os.path.splitext(user_settings)[0])[-1]
            user_settings = imp.load_source(user_settings_name, user_settings)
        if isinstance(user_settings, types.ModuleType):
            user_settings = dict_from_module(user_settings, lambda key: key.isupper())

        settings = dict(default_settings)
        settings.update(user_settings)
        settings.update(patches)

        self._settings = settings

    def get(self, *args):
        if len(args) == 1: return self._get(args[0])
        elif len(args) == 2: return self._get_with_default(args[0], args[1])
        else:
            raise TypeError, 'get() takes exactly 1 or 2 arguments (%s given)' % len(args)

    def _get(self, key):
        if self._settings.has_key(key):
            return self._settings[key]
        else:
            raise KeyError, key

    def _get_with_default(self, key, default):
        if self._settings.has_key(key):
            return self._settings[key]
        return default

    def __getattr__(self, item):
        return self.get(item)