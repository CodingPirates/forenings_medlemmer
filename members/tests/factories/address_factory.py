from factory import Faker, DjangoModelFactory

from members.models import Address


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
