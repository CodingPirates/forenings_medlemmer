from django.test import TestCase
from members.models import Email
from members.tests.factories import PayableItemFactory
from django.conf import settings


class TestPaymentEmails(TestCase):
    def test_payment_confirmation_email(self):
        # Tests that either membership, activty or season is passed
        settings.EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
        payment = PayableItemFactory.create()
        print(settings.BASE_DIR)
        print(Email.send_payment_confirmation(payment))
