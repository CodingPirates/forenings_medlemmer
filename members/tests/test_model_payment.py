from django.test import TestCase
from members.models.payment import Payment
from datetime import datetime
from freezegun import freeze_time

from members.tests.factories import PaymentFactory, TIMEZONE


class TestModelPayment(TestCase):
    def test_can_create_payment(self):
        PaymentFactory() # no error expected

    def test_can_create_refund(self):
        # Create a payment
        payment = PaymentFactory(status="NEW", amount_ore=50000)

        # Create a refund
        PaymentFactory(external_id=payment.external_id, status="REFUND", amount_ore=-50000)
        # should not give any errors