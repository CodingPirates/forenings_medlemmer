from members.tests.factories.factory_helpers import TIMEZONE
from members.models import Payment
from members.tests.factories.activity_factory import ActivityFactory
from members.tests.factories.activity_participant_factory import (
    ActivityParticipantFactory,
)
from members.tests.factories.person_factory import PersonFactory
from members.tests.factories.family_factory import FamilyFactory
from factory.fuzzy import FuzzyInteger
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    payment_type = Faker("payment_type")
    activity = SubFactory(ActivityFactory)
    activityparticipant = SubFactory(ActivityParticipantFactory)
    person = SubFactory(PersonFactory)
    family = SubFactory(FamilyFactory)
    body_text = Faker("text")
    amount_ore = FuzzyInteger(10000, 70000)
    confirmed_at = Faker("date_time", tzinfo=TIMEZONE)
    cancelled_at = Faker("date_time", tzinfo=TIMEZONE)
    refunded_at = Faker("date_time", tzinfo=TIMEZONE)
    rejected_at = Faker("date_time", tzinfo=TIMEZONE)
    reminder_sent_at = Faker("date_time", tzinfo=TIMEZONE)
    rejected_message = Faker("text")
