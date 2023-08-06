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

import re
from django.core.exceptions import ValidationError
from eggplant.utils.string import str2bool


def is_hex(value):
    if re.compile(r'^[a-fA-F0-9]*$').match(value) is None:
        raise ValidationError('%s is not a valid hex string' % value)


def is_integer(raw_value):
    try:
        return int(raw_value)
    except ValueError:
        raise ValidationError('\'%s\' is not an integer.' % raw_value)


def is_positive_integer(raw_value):
    int_value = is_integer(raw_value)
    if int_value <= 0:
        raise ValidationError('\'%s\' is not a positive integer.' % raw_value)
    return int_value


def is_natural_integer(raw_value):
    int_value = is_integer(raw_value)
    if int_value < 0:
        raise ValidationError('\'%s\' is not a natural integer.' % raw_value)
    return int_value


def is_float(raw_value):
    try:
        return float(raw_value)
    except ValueError:
        raise ValidationError('\'%s\' is not a float number.' % raw_value)


def is_positive_float(raw_value):
    float_value = is_float(raw_value)
    if float_value <= 0:
        raise ValidationError('\'%s\' is not a positive float number.' % raw_value)
    return float_value


def is_natural_float(raw_value):
    float_value = is_float(raw_value)
    if float_value < 0:
        raise ValidationError('\'%s\' is not a natural float.' % raw_value)
    return float_value


def is_boolean(raw_value):
    try:
        return str2bool(raw_value)
    except ValueError:
        raise ValidationError('\'%s\' is not a valid boolean value.' % raw_value)

