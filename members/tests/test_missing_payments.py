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

        # Tests (* means: Missing payment)
        #   A: Activityprice = 0
        #   A1: participant with price = 0 without payment
        # * A2: participant with price > 0, no payment
        #   A3: participant with price > 0, payment confirmed
        # * A4: participant with price > 0, payment not confirmed

        #   B: Activityprice = 100
        #   B1: participant with price = 0
        # * B2: participant with payment > 0, no payment
        #   B3: participant with payment > 0, confirmed
        # * B4: participant with payment > 0, not confirmed

        family = FamilyFactory()
        persons = []
        for i in range(8):
            person = PersonFactory(
                family=family,
                birthday=datetime.now() - relativedelta(years=8 + i),
                name=f"person{i + 1}",
            )
            persons.append(person)
        (
            person_1,
            person_2,
            person_3,
            person_4,
            person_5,
            person_6,
            person_7,
            person_8,
        ) = persons

        activity1 = ActivityFactory(
            price_in_dkk=0,
            start_date=datetime.now() - relativedelta(days=2),
            end_date=datetime.now() + relativedelta(days=10),
            min_age=6,
            max_age=20,
        )
        activity2 = ActivityFactory(
            price_in_dkk=100,
            start_date=datetime.now() - relativedelta(days=2),
            end_date=datetime.now() + relativedelta(months=1),
            min_age=6,
            max_age=20,
        )

        # Activity 1: price = 0
        # A1: participant with price = 0 without payment
        participant_a1 = ActivityParticipantFactory(
            person=person_1,
            activity=activity1,
            price_in_dkk=0,
        )

        # A2: participant with price > 0, no payment
        participant_a2 = ActivityParticipantFactory(
            person=person_2,
            activity=activity1,
            price_in_dkk=100,
        )

        # A3: participant with price > 0, payment confirmed
        participant_a3 = ActivityParticipantFactory(
            person=person_3,
            activity=activity1,
            price_in_dkk=100,
        )
        PaymentFactory(
            payment_type=Payment.CREDITCARD,
            activity=activity1,
            activityparticipant=participant_a3,
            person=person_3,
            family=family,
            amount_ore=10000,
            accepted_at=timezone.now(),
            confirmed_at=timezone.now(),
        )

        # participant with price > 0, payment not confirmed
        participant_a4 = ActivityParticipantFactory(
            person=person_4,
            activity=activity1,
            price_in_dkk=100,
        )

        PaymentFactory(
            payment_type=Payment.CREDITCARD,
            activity=activity1,
            activityparticipant=participant_a4,
            person=person_4,
            family=family,
            amount_ore=10000,
            accepted_at=timezone.now(),
            confirmed_at=None,  # Not confirmed
        )

        # Activity 2: price = 100
        # B1: participant with price = 0 kr
        participant_b1 = ActivityParticipantFactory(
            person=person_5,
            activity=activity2,
            price_in_dkk=0,
        )

        # B2: participant with payment > 0, no payment
        participant_b2 = ActivityParticipantFactory(
            person=person_6,
            activity=activity2,
            price_in_dkk=100,
        )

        # B3: participant with payment > 0, confirmed
        participant_b3 = ActivityParticipantFactory(
            person=person_7,
            activity=activity2,
            price_in_dkk=100,
        )
        PaymentFactory(
            payment_type=Payment.CREDITCARD,
            activity=activity2,
            activityparticipant=participant_b3,
            person=person_7,
            family=family,
            amount_ore=5000,
            accepted_at=timezone.now(),
            confirmed_at=timezone.now(),
        )

        # B4: participant with payment > 0, not confirmed
        participant_b4 = ActivityParticipantFactory(
            person=person_8,
            activity=activity2,
            price_in_dkk=50,
        )
        PaymentFactory(
            payment_type=Payment.CREDITCARD,
            activity=activity2,
            activityparticipant=participant_b4,
            person=person_8,
            family=family,
            amount_ore=5000,
            accepted_at=timezone.now(),
            confirmed_at=None,  # Not confirmed
        )

        missing_payments = ActivityParticipant.get_missing_payments_for_family(
            family.id
        )
        # Check missing payments for activity 1
        with self.subTest("1: participant with price = 0 without payment"):
            self.assertNotIn(participant_a1, missing_payments)

        with self.subTest("A2: participant with price > 0, no payment"):
            self.assertIn(participant_a2, missing_payments)

        with self.subTest("A3: participant with price > 0, payment confirmed"):
            self.assertNotIn(participant_a3, missing_payments)

        with self.subTest("A4: participant with price > 0, payment not confirmed"):
            self.assertIn(participant_a4, missing_payments)

        # Check missing payments for activity 2
        with self.subTest("B1: participant with price = 0"):
            self.assertNotIn(participant_b1, missing_payments)

        with self.subTest("B2: participant with payment > 0, no payment"):
            self.assertIn(participant_b2, missing_payments)

        with self.subTest("B3: participant with payment > 0, confirmed"):
            self.assertNotIn(participant_b3, missing_payments)

        with self.subTest("B4: participant with payment > 0, not confirmed"):
            self.assertIn(participant_b4, missing_payments)
