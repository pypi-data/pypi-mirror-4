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
from eggplant.utils.json import json_model_dict


class DictModel(models.Model):
    """
    An abstract model to make Models have dictionary-like interface
    """

    def __getitem__(self, key):
        if key in self.fields:
            return getattr(self, key)
        else:
            raise KeyError, '%s is not a field.' % key

    def __setitem__(self, key, value):
        if key in self.fields:
            return setattr(self, key, value)
        else:
            raise KeyError, '%s is not a field.' % key

    def __contains__(self, item):
        return item in self.keys()

    def has_key(self, k):
        return k in self.keys()

    def items(self):
        return [(field.name, self[field.name]) for field in self.__class__._meta.fields]

    def keys(self):
        return self.fields

    def values(self):
        return [self[field.name] for field in self.__class__._meta.fields]

    @property
    def fields(self):
        """Get a list containing all fields in this model
        :return: a list containing the name of fields in this model
        """
        if not hasattr(self, '_fields') or self._fields is None:
            self._fields = [field.name for field in self.__class__._meta.fields]
        return self._fields

    def dict(self, json_serializable=False, expand_choices=False, **kwargs):
        """Convert a model into dict
        :return: a dictionary containing fields name and values in this model
        """
        if json_serializable:
            json_serializable_fields = [field.name for field in self.__class__._meta.fields
                if not isinstance(field, (models.OneToOneField, models.ManyToManyField, models.ForeignKey))]
            result = dict([item for item in self.items() if item[0] in json_serializable_fields])
        else:
            result = dict(self.items())

        if expand_choices:
            for field, value in result.items():
                if hasattr(self, 'get_%s_display'%field.lower()):
                    result[field] = getattr(self, 'get_%s_display'%field.lower())()

        return result

    def json_dict(self, use_float_seconds=True, summary=False, **kwargs):
        """Convert a model into dict which is json serializable.

        DateTimeField and DateField will be converted into a unix-timestamp-like object.
        Standard unix-timestamp doesn't contain float seconds, but the one returned contains float seconds.

        TimeField will be converted into seconds from 0:00:00

        :return: a dictionary which is json serializable
        """
        return json_model_dict(
            self.dict(json_serializable=True, summary=summary, **kwargs),
            use_float_seconds=use_float_seconds
        )

    class Meta:
        abstract = True
        app_label = APP_LABEL
