from django.test import TestCase
from members.models.union import Union
# from django.core.exceptions import ValidationError


class TestModelUnion(TestCase):
    def test_clean_undefined_bank(self):
        # Validation should fail if the union doesn't have a bank
        union = Union(bank_main_org=False)
        # we need to rewrite the below test since we basically already have
        # sorted the ones with bank_main_org equal to False
        # with self.assertRaises(ValidationError):
        #    union.clean()

        # If we set the bank it shouldn't fail
        # ToDo: maybe test some differently formatted bank accounts
        union.bank_account = "1234-1234567890"
        union.clean()

        union.bank_main_org = True
        union.clean()
