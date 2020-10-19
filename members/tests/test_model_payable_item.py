from django.core.exceptions import ValidationError
from requests.exceptions import HTTPError

from django.test import TestCase
from members.models import PayableItem
from members.models.payable_item import _set_quickpay_order_id
from .factories import PersonFactory, PayableItemFactory


class TestPayableItem(TestCase):
    def test_set_quickpay_order_id(self):
        # Tests that the quickpay order id is set to something uniqe in dev/test
        # and count in prod
        p1 = PayableItemFactory.create()
        with self.settings(PAYMENT_ID_PREFIX="prod"):
            id1 = _set_quickpay_order_id()
        p2 = PayableItemFactory.create()
        with self.settings(PAYMENT_ID_PREFIX="prod"):
            id2 = _set_quickpay_order_id()

        self.assertLess(p1.quick_pay_order_id, p2.quick_pay_order_id)
        self.assertLess(id1, id2)

    def test_get_cant_create_empty(self):
        # Tests that either membership, activty or season is passed
        person = PersonFactory.create()
        with self.assertRaises(ValidationError):
            PayableItem.objects.create(person=person, amount_ore=7500)

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

    def test_get_item(self):
        # Tests that we can retrive both the paid item and the name.
        payment = PayableItemFactory.create()
        self.assertEqual(payment.get_item(), payment.membership)
        self.assertEqual(payment.get_item_name(), "Medlemsskab")

    def test_show_amount(self):
        # Tests that we can retrive both the paid item and the name.
        payment = PayableItemFactory.create(amount_ore=10000)
        self.assertEqual(payment.show_amount(), "100,00")

    def test_amount_less_than_1kr(self):
        # Tests that we can retrive both the paid item and the name.
        with self.assertRaises(ValidationError):
            PayableItemFactory.create(amount_ore=10)

    def test_cant_connect_to_quickpay(self):
        with self.settings(QUICKPAY_URL="http://test.com/"):
            with self.assertRaises(HTTPError):
                PayableItemFactory.create()

        payment = PayableItemFactory.create()
        with self.settings(QUICKPAY_URL="http://test.com/"):
            with self.assertRaises(HTTPError):
                payment.get_link()

    def test_to_string(self):
        payment = PayableItemFactory()
        payment_string = str(payment)
        self.assertIn(str(payment.person), payment_string)
        self.assertIn(str(payment.show_amount()), payment_string)
        self.assertIn(str(payment.get_item()), payment_string)
