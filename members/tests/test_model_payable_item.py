from django.core.exceptions import ValidationError

from django.test import TestCase
from members.models import PayableItem
from .factories import MembershipFactory, PersonFactory, PayableItemFactory


class TestPayableItem(TestCase):
    def test_get_cant_create_empty(self):
        # Tests that either membership, activty or season is passed
        person = PersonFactory.create()
        with self.assertRaises(ValidationError):
            PayableItem.objects.create(person=person, amount_ore=7500)

    def test_increasing_ids(self):
        # Tests that IDS are made automatically set in increaseing order
        membership1 = MembershipFactory.create()
        p1 = PayableItem.objects.create(
            person=membership1.person, amount_ore=7500, membership=membership1
        )
        p2 = PayableItem.objects.create(
            person=membership1.person, amount_ore=7500, membership=membership1
        )
        self.assertGreater(p2.quick_pay_id, p1.quick_pay_id)

    def test_try_to_change_quickpay_id(self):
        # Creates a payment item and tries to change the ID which should fail
        payment = PayableItemFactory.create()
        payment.quick_pay_id = "something else"
        with self.assertRaises(ValidationError):
            payment.save()

        payment = PayableItemFactory.create()
        payment.quick_pay_order_id = "something else"
        with self.assertRaises(ValidationError):
            payment.save()

    def test_get_payment_link(self):
        # Creates a payment item and gets a payment link
        payment = PayableItemFactory.create()
        link = payment.get_link()
        self.assertTrue("https://payment.quickpay.net/payments" in link)

    def test_get_payment_status(self):
        # Tests that we can get a payment status
        payment = PayableItemFactory.create()
        self.assertEqual(payment.get_status(), "initial")
