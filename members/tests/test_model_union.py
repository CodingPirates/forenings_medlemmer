from django.test import TestCase
from django.core.exceptions import ValidationError

from members.tests.factories import UnionFactory, PersonFactory
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
        self.assertEqual("Foreningen for " + union.name, str(union))

    def test_user_union_leader(self):
        union = UnionFactory()

        super_user = PersonFactory.create()
        super_user.user.is_superuser = True
        super_user.user.save()

        user_board_position = PersonFactory.create()
        union.chairman = user_board_position
        union.save()

        user_board_member = PersonFactory.create()
        union.board_members.add(user_board_member)
        union.save()

        normal_user = PersonFactory()
        user_is_none = PersonFactory()
        user_is_none.user = None

        self.assertTrue(union.user_union_leader(super_user.user))
        self.assertTrue(union.user_union_leader(user_board_position.user))
        self.assertTrue(union.user_union_leader(user_board_member.user))
        self.assertFalse(union.user_union_leader(normal_user.user))
        self.assertFalse(union.user_union_leader(user_is_none.user))
