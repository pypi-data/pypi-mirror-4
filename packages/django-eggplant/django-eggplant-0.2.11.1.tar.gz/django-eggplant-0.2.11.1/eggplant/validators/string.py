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

from django.core.exceptions import ValidationError

def is_integer(raw_value):
    try:
        int(raw_value)
    except ValueError:
        raise ValidationError('\'%s\' is not an integer.'%raw_value)

def is_positive_integer(raw_value):
    is_integer(raw_value)
    if int(raw_value) <= 0:
        raise ValidationError('\'%s\' is not a positive integer.'%raw_value)

def is_natural_integer(raw_value):
    is_integer(raw_value)
    if int(raw_value) < 0:
        raise ValidationError('\'%s\' is not a natural integer.'%raw_value)

def is_float(raw_value):
    try:
        float(raw_value)
    except ValueError:
        raise ValidationError('\'%s\' is not a float number.'%raw_value)

def is_positive_float(raw_value):
    is_float(raw_value)
    if float(raw_value) <= 0:
        raise ValidationError('\'%s\' is not a positive float number.'%raw_value)

def is_natural_float(raw_value):
    is_float(raw_value)
    if float(raw_value) < 0:
        raise ValidationError('\'%s\' is not a natural float.'%raw_value)
