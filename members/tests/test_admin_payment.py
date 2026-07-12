from django.contrib.admin import AdminSite
from django.test import TestCase
from django.utils.translation import override

from members.admin.payment_admin import PaymentAdmin
from members.models import Payment


class PaymentAdminTest(TestCase):
    def test_get_payment_amount_uses_two_decimals_and_danish_separator(self):
        payment_admin = PaymentAdmin(Payment, AdminSite())
        payment = Payment(amount_ore=123456)

        with override("da"):
            self.assertEqual(
                str(payment_admin.get_payment_amount(payment)),
                '<span class="payment-amount">1234,56</span>',
            )
