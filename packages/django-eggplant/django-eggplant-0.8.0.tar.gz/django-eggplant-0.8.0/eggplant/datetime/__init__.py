import datetime
import sys
from pytz import timezone
from django.conf import settings

current_timezone = timezone(settings.TIME_ZONE)


def now_with_timezone():
    return datetime.datetime.now().replace(tzinfo=current_timezone)


def total_seconds(td):
    if sys.version_info < (2, 7):
        # timedelta has no total_seconds
        return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / float(10 ** 6)
    else:
        return td.total_seconds()
