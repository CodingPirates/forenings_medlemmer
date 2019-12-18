from django.test import TestCase
from django.core.exceptions import ValidationError
from members.models.payment import Payment
from datetime import datetime
from freezegun import freeze_time

from members.tests.factories import PaymentFactory


class TestModelPayment(TestCase):
    def test_can_create_payment(self):
        PaymentFactory()  # should not throw errors
