import datetime
from django.utils.timezone import is_naive
from django.conf import settings
from pytz import timezone
from six import PY3

CURRENT_TZ = timezone(settings.TIME_ZONE)


def timestamp(raw_datetime, use_float_seconds=False):
    timestamp_format = '%s.%f' if use_float_seconds else '%s'
    if use_float_seconds:
        result_type = float
    else:
        result_type = long if not PY3 else int

    if is_naive(raw_datetime):
        target_datetime = raw_datetime
    else:
        # Since python's strftime('%s') doesn't respect tzinfo,
        # we convert it back to our current timezone first.
        target_datetime = raw_datetime.astimezone(CURRENT_TZ)

    return result_type(target_datetime.strftime(timestamp_format))


def time_to_seconds(time_object, use_float_seconds=False):
    seconds = time_object.hour*3600 + time_object.minute*60 + time_object.second
    if use_float_seconds: seconds += time_object.microsecond/1000000.0
    return seconds


def time_to_utc_seconds(time_object, use_float_seconds=False):
    raw_seconds = time_to_seconds(time_object, use_float_seconds=use_float_seconds)

    if time_object.tzinfo is None:
        # Naive
        utc_diff_seconds = (datetime.datetime.now() - datetime.datetime.utcnow()).total_seconds()
        seconds = raw_seconds - utc_diff_seconds
    else:
        # Aware
        seconds = raw_seconds - time_object.tzinfo._utcoffset.total_seconds()

    return seconds
