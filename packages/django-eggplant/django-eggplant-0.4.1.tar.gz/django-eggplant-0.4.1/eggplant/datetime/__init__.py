import datetime
from pytz import timezone
from django.conf import settings

current_timezone = timezone(settings.TIME_ZONE)

def now_with_timezone():
    return datetime.datetime.now().replace(tzinfo=current_timezone)
