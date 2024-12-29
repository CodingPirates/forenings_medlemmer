import random
from members.tests.factories.factory_helpers import TIMEZONE
from members.models import ActivityParticipant
from members.tests.factories.activity_factory import ActivityFactory
from members.tests.factories.person_factory import PersonFactory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory


class ActivityParticipantFactory(DjangoModelFactory):
    class Meta:
        model = ActivityParticipant

    added_at = Faker("date_time", tzinfo=TIMEZONE)
    activity = SubFactory(ActivityFactory)
    person = SubFactory(PersonFactory)
    note = Faker("text")
    photo_permission = "OK" if random.randint(0, 1) == 1 else "NO"
