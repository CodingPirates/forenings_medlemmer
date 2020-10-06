from members.models import Member
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from members.tests.factories.factory_helpers import TIMEZONE
from members.tests.factories.person_factory import PersonFactory
from members.tests.factories.department_factory import DepartmentFactory


class MemberFactory(DjangoModelFactory):
    class Meta:
        model = Member

    department = SubFactory(DepartmentFactory)
    person = SubFactory(PersonFactory)
    member_since = Faker("date_time", tzinfo=TIMEZONE)
