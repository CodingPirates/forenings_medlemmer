from factory import Faker, SubFactory, LazyAttribute
from factory.django import DjangoModelFactory
from members.models import Department
from members.tests.factories.union_factory import UnionFactory
from members.tests.factories.address_factory import AddressFactory
from members.tests.factories.factory_helpers import (
    TIMEZONE,
    datetime_after,
)


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department

    name = Faker("city")
    description = Faker("text")
    open_hours = Faker("numerify", text="kl. ##:##-##:##")
    responsible_name = Faker("name")
    department_email = Faker("email")
    created = Faker("date_time", tzinfo=TIMEZONE)
    updated_dtm = LazyAttribute(lambda d: datetime_after(d.created))
    closed_dtm = LazyAttribute(lambda d: datetime_after(d.created))
    isVisible = Faker("boolean")
    isOpening = Faker("boolean")
    has_waiting_list = Faker("boolean")
    website = Faker("url")
    union = SubFactory(UnionFactory)
    address = SubFactory(AddressFactory)
