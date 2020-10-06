from factory import Faker
from factory.django import DjangoModelFactory

from members.models import Address
from factory.fuzzy import FuzzyChoice


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    city = Faker("city")
    zipcode = Faker("zipcode")
    municipality = Faker("municipality")
    longitude = Faker("longitude")
    latitude = Faker("latitude")
    region = FuzzyChoice([r[0] for r in Address.REGION_CHOICES])
