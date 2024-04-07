from factory import Faker
from factory.django import DjangoModelFactory
from members.models import Family
from members.tests.factories.factory_helpers import TIMEZONE


class FamilyFactory(DjangoModelFactory):
    class Meta:
        model = Family

    unique = Faker("uuid4")
    email = Faker("email")
    # dont_send_mails = Faker("boolean")
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    confirmed_at = Faker("date_time", tzinfo=TIMEZONE)
    last_visit_dtm = Faker("date_time", tzinfo=TIMEZONE)
    deleted_dtm = Faker("date_time", tzinfo=TIMEZONE)
