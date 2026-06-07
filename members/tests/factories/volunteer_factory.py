from members.tests.factories.factory_helpers import TIMEZONE
from members.models import Volunteer
from members.tests.factories.person_factory import PersonFactory
from members.tests.factories.department_factory import DepartmentFactory
from factory import Faker, SubFactory, LazyAttribute
from factory.django import DjangoModelFactory
from members.tests.factories.factory_helpers import datetime_after


class VolunteerFactory(DjangoModelFactory):
    class Meta:
        model = Volunteer

    person = SubFactory(PersonFactory)
    department = SubFactory(DepartmentFactory)

    added_at = Faker("date_time", tzinfo=TIMEZONE)
    confirmed = LazyAttribute(lambda d: datetime_after(d.added_at))
    removed = LazyAttribute(lambda d: datetime_after(d.added_at))
