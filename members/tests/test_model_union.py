from django.test import TestCase
from django.core.exceptions import ValidationError

from members.tests.factories import UnionFactory
from members.models import Union


class TestModelUnion(TestCase):
    def test_defaults_to_having_an_account_at_main_org(self):
        union = Union()
        self.assertTrue(union.bank_main_org)

    def test_bank_account_not_required_if_account_at_main_org(self):
        union = UnionFactory(bank_main_org=True, bank_account="")
        union.clean()  # Should not raise error

    def test_bank_account_required_if_no_account_at_main_org(self):
        union = UnionFactory(bank_main_org=False, bank_account="")

        with self.assertRaises(ValidationError):
            union.clean()

    def test_bank_account_correct_format0(self):
        union = UnionFactory(bank_main_org=False, bank_account="4723-4382732")
        union.clean()  # Should not raise error

    def test_bank_account_correct_format1(self):
        union = UnionFactory(bank_main_org=False, bank_account="4723-0438273223")
        union.clean()  # Should not raise error

    def test_string_representation(self):
        union = UnionFactory()
        self.assertEqual(union.name, str(union))
