from factory import Faker
from factory.django import DjangoModelFactory
from members.models.municipality import Municipality


class MunicipalityFactory(DjangoModelFactory):
    class Meta:
        model = Municipality

    name = Faker("name")
    address = Faker("address")
    zipcode = Faker("zipcode")
    city = Faker("city")
    dawa_id = Faker("uuid4")
