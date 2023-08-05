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