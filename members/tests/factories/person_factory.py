import factory
from factory import Faker, SubFactory, SelfAttribute
from factory.django import DjangoModelFactory
from members.models.municipality import Municipality
from members.tests.factories.factory_helpers import TIMEZONE, LOCALE
from members.tests.factories.providers import DanishProvider
from factory.fuzzy import FuzzyChoice
from members.models import Person
from members.tests.factories.family_factory import FamilyFactory
from members.tests.factories.user_factory import UserFactory

Faker.add_provider(DanishProvider, locale=LOCALE)
Faker._DEFAULT_LOCALE = "dk_DK"


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    membertype = "PA"
    name = Faker("name")
    placename = Faker("city_suffix")
    zipcode = Faker("zipcode")
    city = Faker("city")
    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    dawa_id = Faker("uuid4")
    municipality = factory.Iterator(Municipality.objects.all())
    longitude = Faker("longitude")
    latitude = Faker("latitude")
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    email = factory.Sequence(
        lambda n: "person{0}@example.com".format(n)
    )  # Faker("email")
    phone = Faker("phone_number")
    gender = FuzzyChoice([code for (code, name) in Person.MEMBER_GENDER_CHOICES])
    birthday = Faker("date")
    # has_certificate = Faker("date")
    family = SubFactory(FamilyFactory, email=email)
    notes = Faker("text")
    # added_at = Faker("date_time", tzinfo=TIMEZONE)
    # deleted_dtm = Faker("date_time", tzinfo=TIMEZONE)
    user = SubFactory(
        UserFactory, username=SelfAttribute("..email"), email=SelfAttribute("..email")
    )
    address_invalid = Faker("boolean")
