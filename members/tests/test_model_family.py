from django.test import TestCase
from members.models.family import Family
from members.jobs import EmailSendCronJob
from django.core import mail


class TestModelFamily(TestCase):
    fixtures = ['departments', 'templates', 'unions']

    def test_unique_is_unique(self):
        family1 = Family()
        family2 = Family()
        self.assertFalse(family1.unique == family2, "Instances of the Family models does have a unique value in the unique field")

    def test_email_link(self):
        family = Family(email="test@example.com")
        family.save()
        family.send_link_email()
        EmailSendCronJob().do()
        self.assertEqual(len(mail.outbox), 1, msg="Email wasn't")
