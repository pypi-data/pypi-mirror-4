import datetime
from eggplant.utils.timezone import utc_timestamp, time_to_seconds

def json_model_dict(raw_object, use_float_seconds=True):
    result = dict(raw_object)

    # DateTimeField and DateField
    datetime_pairs = [(key, utc_timestamp(value, use_float_seconds=use_float_seconds))
                      for key, value in result.items() if isinstance(value, datetime.date)]
    result.update(datetime_pairs)

    # TimeField
    time_pairs = [(key, time_to_seconds(value, use_float_seconds=use_float_seconds))
                  for key, value in result.items() if isinstance(value, datetime.time)]
    result.update(time_pairs)

    return result
