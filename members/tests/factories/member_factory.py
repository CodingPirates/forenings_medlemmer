from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from members.models.member import Member
from members.tests.factories.factory_helpers import TIMEZONE
from members.tests.factories.person_factory import PersonFactory
from members.tests.factories.union_factory import UnionFactory

class MemberFactory(DjangoModelFactory):
    class Meta:
        model = Member

    member_since = Faker("date_time", tzinfo=TIMEZONE)
    member_until = Faker("date_time", tzinfo=TIMEZONE)
    price_in_dkk = Faker("random_number", digits=4)
    person = SubFactory(PersonFactory)
    union = SubFactory(UnionFactory)
    paid_at = Faker("date_time", tzinfo=TIMEZONE)
