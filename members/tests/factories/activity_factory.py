import factory
from members.tests.factories.factory_helpers import TIMEZONE, LOCALE
from members.tests.factories.providers import DanishProvider, CodingPiratesProvider
from members.models import Activity
from members.tests.factories.union_factory import UnionFactory
from members.tests.factories.department_factory import DepartmentFactory
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
    placename = Faker("city_suffix")
    zipcode = Faker("zipcode")
    city = Faker("city")
    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    dawa_id = Faker("uuid4")
    description = Faker("text")
    instructions = Faker("text")
    signup_closing = Faker("date_time", tzinfo=TIMEZONE)
    start_date = LazyAttribute(
        lambda d: datetime_before(d.now)
        if d.active
        else Faker("date_time", tzinfo=TIMEZONE).generate({})
    )
    end_date = LazyAttribute(
        lambda d: datetime_after(d.now) if d.active else datetime_before(d.now)
    )
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    open_invite = Faker("boolean")
    price_in_dkk = Faker("random_number", digits=4)
    max_participants = Faker("random_number")
    min_age = Faker("random_number")
    max_age = LazyAttribute(lambda a: a.min_age + Faker("random_number").generate({}))
    member_justified = Faker("boolean")
