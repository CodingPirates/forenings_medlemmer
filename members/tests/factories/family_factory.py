from factory import Faker, DjangoModelFactory
from factory.fuzzy import FuzzyAttribute
import factory
from members.models import Family
from members.tests.factories.factory_helpers import TIMEZONE


class FamilyFactory(DjangoModelFactory):
    class Meta:
        model = Family

    unique = Faker("uuid4")
    # email = Faker("email")
    email = FuzzyAttribute(
        lambda: f"family{Family.objects.all().count() + 1}@example.com"
    )
    # dont_send_mails = Faker("boolean")
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    confirmed_dtm = Faker("date_time", tzinfo=TIMEZONE)
    last_visit_dtm = Faker("date_time", tzinfo=TIMEZONE)
    deleted_dtm = Faker("date_time", tzinfo=TIMEZONE)
