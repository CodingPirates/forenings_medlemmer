from factory import Faker
from factory.django import DjangoModelFactory

from members.models import Consent
from members.tests.factories.factory_helpers import TIMEZONE


class ConsentFactory(DjangoModelFactory):
    class Meta:
        model = Consent

    released_at = Faker("date_time", tzinfo=TIMEZONE)
    title = Faker("sentence")
    text = Faker("text")
