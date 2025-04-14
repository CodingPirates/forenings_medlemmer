from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.test import TestCase

from members.models.activityparticipant import ActivityParticipant
from members.models.payment import Payment

from .factories import (
    FamilyFactory,
    PersonFactory,
    ActivityFactory,
    ActivityParticipantFactory,
    PaymentFactory,
)


class TestMissingPayments(TestCase):
    def test_payments_for_family(self):
        # Arrange
        # 2 persons, 1 paid, 1 not paid
        family = FamilyFactory()
        person_paid = PersonFactory(
            family=family,
            birthday=datetime.now() - relativedelta(years=10),
        )
        person_not_paid = PersonFactory(
            family=family,
            birthday=datetime.now() - relativedelta(years=12),
        )
        activity = ActivityFactory(
            price_in_dkk=100,
            start_date=datetime.now() - relativedelta(days=2),
            end_date=datetime.now() + relativedelta(months=1),
            min_age=7,
            max_age=17,
        )
        participant_paid = ActivityParticipantFactory(
            person=person_paid,
            activity=activity,
        )
        participant_not_paid = ActivityParticipantFactory(
            person=person_not_paid,
            activity=activity,
        )
        PaymentFactory(
            payment_type=Payment.CREDITCARD,
            activity=activity,
            activityparticipant=participant_paid,
            person=person_paid,
            family=family,
            amount_ore=10000,
            accepted_at=timezone.now(),
            confirmed_at=timezone.now(),
        )

        # Act
        missing_payments = ActivityParticipant.get_missing_payments_for_family(
            family.id
        )

        # Assert
        self.assertIn(participant_not_paid, missing_payments)
        self.assertNotIn(participant_paid, missing_payments)
