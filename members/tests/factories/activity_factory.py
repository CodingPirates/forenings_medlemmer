import factory
from members.tests.factories.factory_helpers import TIMEZONE, LOCALE
from members.tests.factories.providers import DanishProvider, CodingPiratesProvider
from members.models import Activity
from members.tests.factories.union_factory import UnionFactory
from members.tests.factories.department_factory import DepartmentFactory
from members.tests.factories.address_factory import AddressFactory
from django.utils import timezone
from factory import Faker, SubFactory, LazyAttribute
from factory.django import DjangoModelFactory
from members.tests.factories.factory_helpers import (
    datetime_after,
    datetime_before,
)


Faker.add_provider(DanishProvider, locale=LOCALE)
Faker.add_provider(CodingPiratesProvider, locale="dk_DK")
Faker._DEFAULT_LOCALE = "dk_DK"


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = Activity
        exclude = ("active", "now")

    # Helper fields
    active = Faker("boolean")
    now = timezone.now()

    union = SubFactory(UnionFactory)
    department = SubFactory(DepartmentFactory, union=factory.SelfAttribute("..union"))
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
        lambda d: (
            datetime_before(d.now)
            if d.active
            else Faker("date_time", tzinfo=TIMEZONE).generate({})
        )
    )
    end_date = LazyAttribute(
        lambda d: datetime_after(d.now) if d.active else datetime_before(d.now)
    )
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    open_invite = Faker("boolean")
    price_in_dkk = Faker("random_number", digits=4)
    max_participants = Faker("random_number")
    min_age = Faker("random_int", min=5, max=18)
    max_age = LazyAttribute(
        lambda a: a.min_age + Faker("random_int", min=10, max=80).generate({})
    )
    member_justified = Faker("boolean")
    address = SubFactory(AddressFactory)
