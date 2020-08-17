import random
from members.tests.factories.factory_helpers import TIMEZONE
from members.models import ActivityParticipant
from members.tests.factories.activity_factory import ActivityFactory
from members.tests.factories.member_factory import MemberFactory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory


class ActivityParticipantFactory(DjangoModelFactory):
    class Meta:
        model = ActivityParticipant

    added_dtm = Faker("date_time", tzinfo=TIMEZONE)
    activity = SubFactory(ActivityFactory)
    member = SubFactory(MemberFactory)
    note = Faker("text")
    photo_permission = "OK" if random.randint(0, 1) == 1 else "NO"
    contact_visible = Faker("boolean")
