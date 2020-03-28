from django.test import TestCase, override_settings
from members.models.emailtemplate import EmailTemplate
from members.models.family import Family
from members.models.person import Person
from django.core import mail
from members.jobs import EmailSendCronJob

from .factories import DepartmentFactory, UnionFactory


class TestEmailTemplate(TestCase):
    def setUp(self):
        self.template = EmailTemplate(
            idname="TEST",
            name="TEMPLATE NAME",
            description="TEMPLATE DESCRIPTION",
            subject="TEMPLATE SUBJECT",
            body_html="TEMPLATE HTML",
            body_text="TEMPLATE TEXT",
        )
        self.template.save()

        self.family = Family(email="family@example.com")
        self.family.save()

        self.person = Person(family=self.family)
        self.person.save()

        self.union = UnionFactory()
        self.department = DepartmentFactory(
            union=self.union, department_email="department@example.com"
        )

    def util_check_email(self, receivers):
        self.assertEqual(len(mail.outbox), len(receivers))
        self.assertEqual(
            mail.outbox[0].to, receivers, msg="Email receiver is incorrect"
        )
        self.assertEqual(
            mail.outbox[0].from_email,
            "TEST <from@example.com>",
            msg="Email from address is incorrect",
        )
        # Note: breaks if Django decides to swap plain text and html
        self.assertEqual(
            mail.outbox[0].content_subtype,
            "plain",
            msg="Django changed how they handle mail with multiple types (Plain text version broke)",
        )
        self.assertEqual(mail.outbox[0].body, "TEMPLATE TEXT")
        self.assertEqual(
            mail.outbox[0].alternatives[0][1],
            "text/html",
            msg="Django changed how they handle mail with multiple types (HTML version broke)",
        )
        self.assertEqual(mail.outbox[0].alternatives[0][0], "TEMPLATE HTML")

    @override_settings(SITE_CONTACT="TEST <from@example.com>")
    def test_send_email_family(self):
        self.template.makeEmail(self.family, {})
        EmailSendCronJob().do()
        self.util_check_email(["family@example.com"])

    @override_settings(SITE_CONTACT="TEST <from@example.com>")
    def test_send_email_family_no_to_email(self):
        self.family.dont_send_mails = True
        self.family.save()
        self.template.makeEmail(self.family, {})
        EmailSendCronJob().do()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(SITE_CONTACT="TEST <from@example.com>")
    def test_send_email_person(self):
        self.person.email = "person@example.com"
        self.person.save()
        self.template.makeEmail(self.person, {})
        EmailSendCronJob().do()
        self.util_check_email(["person@example.com"])

    @override_settings(SITE_CONTACT="TEST <from@example.com>")
    def test_send_email_person_no_to_email(self):
        self.family.dont_send_mails = True
        self.family.save()
        self.template.makeEmail(self.person, {})
        EmailSendCronJob().do()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(SITE_CONTACT="TEST <from@example.com>")
    def test_send_email_department(self):
        self.template.makeEmail(self.department, {})
        EmailSendCronJob().do()
        self.util_check_email(["department@example.com"])
