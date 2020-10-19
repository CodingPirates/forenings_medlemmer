from factory import DjangoModelFactory, SubFactory
from members.models import Membership

from members.tests.factories.union_factory import UnionFactory
from members.tests.factories.person_factory import PersonFactory


class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = Membership

    union = SubFactory(UnionFactory)
    person = SubFactory(PersonFactory)
