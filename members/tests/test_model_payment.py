from django.test import TestCase
from django.core.exceptions import ValidationError
from members.models.payment import Payment
from datetime import datetime
from freezegun import freeze_time

from members.tests.factories import PaymentFactory, TIMEZONE


class TestModelPayment(TestCase):
    def mock_reference_time(self, time):
        def mock(timezone):
            pass

        return mock

    def test_can_create_payment(self):
        PaymentFactory()  # should not throw errors
