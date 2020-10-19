from factory import DjangoModelFactory, SubFactory
from members.models import PayableItem
from factory.fuzzy import FuzzyInteger

from members.tests.factories.membership_factory import MembershipFactory
from members.tests.factories.person_factory import PersonFactory


class PayableItemFactory(DjangoModelFactory):
    class Meta:
        model = PayableItem

    person = SubFactory(PersonFactory)
    amount_ore = FuzzyInteger(7500, 200000)
    membership = SubFactory(MembershipFactory)
