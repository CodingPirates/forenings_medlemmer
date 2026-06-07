import random

from django.utils import timezone
from factory import Faker, LazyAttribute, SubFactory
from factory.django import DjangoModelFactory

from forenings_medlemmer.settings import MINIMUM_SEASON_PRICE_IN_DKK
from members.models import Activity
from members.tests.factories.address_factory import AddressFactory
from members.tests.factories.department_factory import DepartmentFactory
from members.tests.factories.factory_helpers import (
    LOCALE,
    TIMEZONE,
    datetime_after,
    datetime_before,
)
from members.tests.factories.providers import CodingPiratesProvider, DanishProvider

Faker.add_provider(DanishProvider, locale=LOCALE)
Faker.add_provider(CodingPiratesProvider, locale="dk_DK")
Faker._DEFAULT_LOCALE = "dk_DK"


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = Activity
        exclude = ("active", "now", "fallback_date")

    # Helper fields
    active = Faker("boolean")
    now = timezone.now()
    fallback_date = Faker("date_time", tzinfo=TIMEZONE)

    department = SubFactory(DepartmentFactory)
    name = Faker("activity")
    open_hours = Faker("numerify", text="kl. ##:00-##:00")
    responsible_name = Faker("name")
    responsible_contact = Faker("email")
    description = Faker("text")
    instructions = Faker("text")
    signup_closing = Faker(
        "date_time_between", tzinfo=TIMEZONE, start_date="-100d", end_date="+100d"
    )
    start_date = LazyAttribute(
        lambda d: datetime_before(d.now) if d.active else d.fallback_date
    )
    end_date = LazyAttribute(
        lambda d: datetime_after(d.now) if d.active else datetime_before(d.now)
    )
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    open_invite = Faker("boolean")
    price_in_dkk = Faker("random_int", min=MINIMUM_SEASON_PRICE_IN_DKK, max=9999)
    max_participants = Faker("random_number")
    min_age = Faker("random_int", min=5, max=18)
    max_age = LazyAttribute(lambda a: a.min_age + random.randint(10, 80))
    address = SubFactory(AddressFactory)
