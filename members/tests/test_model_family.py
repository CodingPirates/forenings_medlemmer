from django.test import TestCase
from django.db.utils import IntegrityError
from django.core import mail
from members.jobs import EmailSendCronJob
from members.models.family import Family
from members.models.person import Person
from members.models.emailtemplate import EmailTemplate

from members.tests.factories import FamilyFactory, PersonFactory


class TestModelFamily(TestCase):
    def test_saving_and_retrieving_family(self):
        family = FamilyFactory()
        PersonFactory(family=family)
        PersonFactory(family=family, membertype=Person.CHILD)

        self.assertEqual(family, Family.objects.first())
        self.assertEqual(1, Family.objects.count())
        self.assertEqual(2, Person.objects.count())

    def test_defaults_to_dont_send_mails(self):
        family = FamilyFactory()
        self.assertFalse(family.dont_send_mails)

    def test_get_first_parent_none_when_no_parents(self):
        family = FamilyFactory()
        PersonFactory(family=family, membertype=Person.CHILD)
        self.assertIsNone(family.get_first_parent())

    def test_get_first_parent(self):
        family = FamilyFactory()
        p1 = PersonFactory(family=family, membertype=Person.PARENT)
        PersonFactory(family=family, membertype=Person.PARENT)
        PersonFactory(family=family, membertype=Person.CHILD)
        self.assertEqual(p1, family.get_first_parent())

    def test_get_first_parent_when_guardian(self):
        family = FamilyFactory()
        p1 = PersonFactory(family=family, membertype=Person.GUARDIAN)
        PersonFactory(family=family, membertype=Person.PARENT)
        PersonFactory(family=family, membertype=Person.PARENT)
        self.assertEqual(p1, family.get_first_parent())

    def test_cannot_create_two_families_with_same_email(self):
        FamilyFactory(email="test@example.com")
        with self.assertRaises(IntegrityError):
            FamilyFactory(email="test@example.com")

    def test_send_login_link_email(self):
        self.template = EmailTemplate(
            idname="LINK",
            name="TEMPLATE NAME",
            description="TEMPLATE DESCRIPTION",
            subject="TEMPLATE SUBJECT",
            body_html="TEMPLATE HTML",
            body_text="TEMPLATE TEXT",
        )
        self.template.save()

        family = FamilyFactory()
        family.send_link_email()
        EmailSendCronJob().do()
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual("TEMPLATE SUBJECT", mail.outbox[0].subject)

    def test_string_representation(self):
        family = FamilyFactory(email="test@example.com")
        self.assertEqual("test@example.com", str(family))

    # TODO: fix get_abosolute_url(), it causes an error (but is not used in the codebase)
    # def test_get_abosolute_url(self):
    #     family = FamilyFactory()
    #     self.assertEqual("family_form", family.get_absolute_url())
