"""
Copyright 2012 Dian-Je Tsai, Cramdroid, and Wantoto Inc

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

from django.core.exceptions import ValidationError, ImproperlyConfigured
from eggplant.validators.string import is_integer


def range_validator(target_value, operator):
    def validator(raw_value):
        raw_value = is_integer(raw_value)

        if operator not in ('==', '!=', '<=', '>=', '<', '>'):
            raise ImproperlyConfigured('Operator is invalid.')

        if (operator == '==' and raw_value == target_value) or\
           (operator == '!=' and raw_value != target_value) or\
           (operator == '<=' and raw_value <= target_value) or\
           (operator == '>=' and raw_value >= target_value) or\
           (operator == '<' and raw_value < target_value) or\
           (operator == '>' and raw_value > target_value):
            return

        raise ValidationError('({0} {1} {2}) is not valid.'.format(raw_value, operator, target_value))
    return validator

