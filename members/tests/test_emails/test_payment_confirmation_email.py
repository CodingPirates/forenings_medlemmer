from django.test import TestCase
from members.models import Email
from members.tests.factories import PayableItemFactory


class TestPaymentEmails(TestCase):
    def test_payment_confirmation_email(self):
        # TODO How to test?
        payment = PayableItemFactory.create()
        Email.send_payment_confirmation(payment)
