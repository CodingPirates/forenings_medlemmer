from members.tests.factories.factory_helpers import TIMEZONE
from members.models import WaitingList
from members.tests.factories.person_factory import PersonFactory
from members.tests.factories.department_factory import DepartmentFactory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory


class WaitingListFactory(DjangoModelFactory):
    class Meta:
        model = WaitingList

    person = SubFactory(PersonFactory)
    department = SubFactory(DepartmentFactory)
    on_waiting_list_since = Faker("date_time", tzinfo=TIMEZONE)
    added_at = Faker("date_time", tzinfo=TIMEZONE)
