from random import randint

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

    def test_get_children(self):
        family = FamilyFactory()
        kids = [
            PersonFactory(membertype=Person.CHILD, family=family)
            for i in range(randint(1, 10))
        ]
        family_kids = family.get_children()
        for kid in kids:
            self.assertTrue(kid in family_kids)
        self.assertEqual(len(kids), len(family_kids))

    # TODO: fix get_abosolute_url(), it causes an error (but is not used in the codebase)
    # def test_get_abosolute_url(self):
    #     family = FamilyFactory()
    #     self.assertEqual("family_form", family.get_absolute_url())

    def create_request_with_permission(self, permission):
        return type(
            "Request",
            (object,),
            {
                "user": type(
                    "User",
                    (object,),
                    {"has_perm": lambda self, perm: perm == permission},
                )()
            },
        )()

    def test_anonymize_family_with_no_members(self):
        family = FamilyFactory(dont_send_mails=False)

        request = self.create_request_with_permission("members.anonymize_persons")
        family.anonymize(request)

        self.assertEquals(family.email, f"anonym-{family.id}@codingpirates.dk")
        self.assertTrue(family.dont_send_mails)
        self.assertTrue(family.anonymized)

    def test_cannot_anonymize_family_with_non_anonymized_members(self):
        family = FamilyFactory()
        PersonFactory(family=family)

        with self.assertRaises(
            Exception,
            msg="Alle personer i en familie skal være anonymiseret, for at familien kan anonymiseres.",
        ):
            family.anonymize()
