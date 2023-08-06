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
import datetime
from eggplant.utils.timezone import timestamp, time_to_seconds


def json_model_dict(raw_object, use_float_seconds=True):
    result = dict(raw_object)

    # DateTimeField and DateField
    datetime_pairs = [(key, timestamp(value, use_float_seconds=use_float_seconds))
                      for key, value in result.items() if isinstance(value, datetime.date)]
    result.update(datetime_pairs)

    # TimeField
    time_pairs = [(key, time_to_seconds(value, use_float_seconds=use_float_seconds))
                  for key, value in result.items() if isinstance(value, datetime.time)]
    result.update(time_pairs)

    return result


def json_model_collection(raw_collection, use_float_seconds=True, **kwargs):
    result = []
    for model in raw_collection:
        result.append(json_model_dict(model.dict(**kwargs), use_float_seconds=use_float_seconds))
    return result
