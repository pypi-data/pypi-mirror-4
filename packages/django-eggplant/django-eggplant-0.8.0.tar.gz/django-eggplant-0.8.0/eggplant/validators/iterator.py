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

from django.core.exceptions import ValidationError
from eggplant.validators.number import range_validator


def len_validator(target_value, operator):
    def validator(raw_value):
        try:
            range_validator(target_value, operator)(len(raw_value))
        except ValidationError:
            raise ValidationError('The length of \'{0}\' {1} {2}'.format(raw_value, operator, target_value))
    return validator
