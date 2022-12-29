import zoneinfo
import random
from datetime import timedelta

from django.conf import settings


LOCALE = "dk_DK"
TIMEZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)
# Setting default locale (this is not documented or intended by factory_boy)
# Faker._DEFAULT_LOCALE = LOCALE


def datetime_before(datetime):
    return datetime - timedelta(days=random.randint(1, 4 * 365))


def datetime_after(datetime):
    return datetime + timedelta(days=random.randint(1, 4 * 365))
