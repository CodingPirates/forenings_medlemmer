import factory
from factory import Faker, DjangoModelFactory, SubFactory
from factory.fuzzy import FuzzyChoice

from members.models import Union
from members.tests.factories import AddressFactory
from members.tests.factories.factory_helpers import TIMEZONE


class UnionFactory(DjangoModelFactory):
    class Meta:
        model = Union

    name = factory.LazyAttribute(lambda u: "Coding Pirates {}".format(u.address.city))
    chairman = Faker("name")
    chairman = Faker("email")
    second_chair = Faker("name")
    second_chair_email = Faker("email")
    cashier = Faker("name")
    cashier_email = Faker("email")
    secretary = Faker("name")
    secratary_email = Faker("email")
    union_email = Faker("email")
    statues = Faker("url")
    founded = Faker("date_time", tzinfo=TIMEZONE)
    region = FuzzyChoice([r[0] for r in Union.regions])
    address = SubFactory(AddressFactory)
    boardMembers = Faker("text")
    bank_main_org = Faker("boolean")
    bank_account = Faker("numerify", text="####-##########")
