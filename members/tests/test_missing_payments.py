from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase

from .factories import (
    FamilyFactory,
    PersonFactory,
    ActivityFactory,
    ActivityParticipantFactory,
    PaymentFactory,
)

from members.views.NonPaidParticipations import get_missing_payments_for_family


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
        payment = PaymentFactory(
            activityparticipant=participant_paid,
            amount_ore=10000,
            confirmed_at=datetime.now(),
        )

        # Act
        missing_payments = get_missing_payments_for_family(family.id)

        # Assert
        self.assertNotIn(participant_paid, missing_payments)
        self.assertIn(participant_not_paid, missing_payments)
