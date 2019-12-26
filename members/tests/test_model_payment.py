from django.test import TestCase

from members.tests.factories import PaymentFactory


class TestModelPayment(TestCase):
    def mock_reference_time(self, time):
        def mock(timezone):
            pass

        return mock

    def test_can_create_payment(self):
        PaymentFactory()  # should not throw errors
