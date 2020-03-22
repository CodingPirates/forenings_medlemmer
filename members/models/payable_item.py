import requests
import json


from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings


def _set_quickpay_order_id():
    return f"{settings.PAYMENT_ID_PREFIX}{timezone.now().timestamp()}"


url = "https://api.quickpay.net/payments"
headers = {
    "accept-version": "v10",
    "content-type": "application/json",
}
auth = ("", settings.QUICKPAY_API_KEY)


class PayableItem(models.Model):
    class Meta:
        verbose_name_plural = "Betalinger"
        verbose_name = "Betaling"
        # ordering = ["address__zipcode"]

    person = models.ForeignKey(
        "Person", on_delete=models.PROTECT, related_name="payments"
    )
    added = models.DateTimeField("Tilføjet", default=timezone.now)
    amount_ore = models.IntegerField("Beløb i øre")

    # Payable items, at least one of them should not be null.
    membership = models.ForeignKey(
        "Membership",
        on_delete=models.PROTECT,
        related_name="payment",
        null=True,
        blank=True,
    )
    quick_pay_order_id = models.CharField(
        "Quick Pay order ID",
        max_length=20,
        unique=True,
        default=_set_quickpay_order_id,
    )
    quick_pay_id = models.IntegerField("Quick Pay ID")
    _payment_link = models.URLField("Betalingslink", null=True, blank=True)

    __original_quick_pay_order_id = None
    __original_quick_pay_id = None

    def __init__(self, *args, **kwargs):
        super(PayableItem, self).__init__(*args, **kwargs)
        self.clean()
        if self.quick_pay_id is None:
            self.__original_quick_pay_order_id = self.quick_pay_order_id
            self.quick_pay_id = self.__create_quickpay_transaction()
            self.__original_quick_pay_id = self.quick_pay_id

    def clean(self):
        if (
            self.__original_quick_pay_id is not None
            and self.quick_pay_id != self.__original_quick_pay_id
        ):
            raise ValidationError(f"{self} tried to change quick_pay_id")
        if (
            self.__original_quick_pay_order_id is not None
            and self.quick_pay_order_id != self.__original_quick_pay_order_id
        ):
            raise ValidationError(f"{self} tried to change quick_pay_order_id")
        if self.membership is None:
            raise ValidationError(f"{self} does not have any membership")
        if self.amount_ore < 100:
            raise ValidationError(
                f"{self.amount} is below 1kr, rember to specify price in øre"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super(PayableItem, self).save(*args, **kwargs)

    def __create_quickpay_transaction(self):
        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            data=json.dumps(
                {
                    "order_id": self.quick_pay_order_id,
                    "currency": "dkk",
                    "text_on_statement": "Coding Pirates",
                }
            ),
        )
        if response.status_code != 201:
            raise requests.HTTPError(
                f"Quick pay payment failed, see:\n {response.text}"
            )
        return response.json()["id"]

    def __str__(self):
        # TODO add season and activty
        return f"Betaling: {self.person} på {self.amount_ore / 100.0}kr, for {self.membership}"

    def get_link(self, continue_url=None):
        if self._payment_link is not None:
            return self._payment_link

        response = requests.put(
            f"{url}/{self.quick_pay_id}/link",
            auth=auth,
            headers=headers,
            data=json.dumps(
                {
                    "amount": self.amount_ore,
                    "language": "da",
                    "auto_capture": True,
                    "continue_url": continue_url
                    # TODO add cancel url
                }
            ),
        )
        if response.status_code != 200:
            raise requests.HTTPError(f"Quick pay link failed, see:\n {response.text}")
        self._payment_link = response.json()["url"]
        return self._payment_link

    def get_status(self):
        response = requests.get(
            f"{url}/{self.quick_pay_id}", auth=auth, headers=headers,
        )
        if response.status_code != 200:
            raise requests.HTTPError(
                f"Quick pay get payment info failed, see:\n {response.text}"
            )
        return response.json()["state"]

    def get_type_name(self):
        if self.membership is not None:
            return self.membership

    def show_amount(self):
        return self.amount_ore / 100


# Do we need this?
#  text = models.TextField("Beskrivelse")
# accepted_dtm = models.DateTimeField("Accepteret", blank=True, null=True)
# confirmed_dtm = models.DateTimeField(
#     "Bekræftet", blank=True, null=True
# )  # Set when paid (and checked)
# cancelled_dtm = models.DateTimeField(
#     "Annulleret", blank=True, null=True
# )  # Set when transaction is cancelled
# refunded_dtm = models.DateTimeField(
#     "Refunderet", blank=True, null=True
# )  # Set when transaction is cancelled
# rejected_dtm = models.DateTimeField(
#     "Afvist", blank=True, null=True
# )  # Set if paiment failed
# rejected_message = models.TextField(
#     "Afvist årsag", blank=True, null=True
# )  # message describing failure
#
# def save(self, *args, **kwargs):
#     is_new = (
#         not self.pk
#     )  # set when calling super, which is needed before we can link to this
#     super_return = super(Payment, self).save(*args, **kwargs)
#
#     """ On creation make quickpay transaction if paymenttype CREDITCARD """
#     if is_new and self.payment_type == Payment.CREDITCARD:
#         quickpay_transaction = members.models.quickpaytransaction.QuickpayTransaction(
#             payment=self, amount_ore=self.amount_ore
#         )
#         quickpay_transaction.save()
#     return super_return
#
# def __str__(self):
#     return str(self.family.email) + " - " + self.body_text
#
# def get_quickpaytransaction(self):
#     return self.quickpaytransaction_set.order_by("-payment__added")[0]
#
# def set_accepted(self):
#     if self.accepted_dtm is None:
#         self.accepted_dtm = timezone.now()
#         self.save()
#
# def set_confirmed(self):
#     # Necessary if payment was autocaptured
#     self.set_accepted()
#     if self.confirmed_dtm is None:
#         self.confirmed_dtm = timezone.now()
#         self.rejected_dtm = None
#         self.rejected_message = None
#         self.save()
#
# def set_rejected(self, message):
#     if self.rejected_dtm is None:
#         self.confirmed_dtm = None
#         self.rejected_dtm = timezone.now()
#         self.rejected_message = message
#         self.save()
#
# @staticmethod
# def capture_oustanding_payments():
#     # get payments that are not confirmed and where activity starts this year
#     payments = Payment.objects.filter(
#         accepted_dtm__isnull=False,
#         rejected_dtm__isnull=True,
#         cancelled_dtm__isnull=True,
#         confirmed_dtm__isnull=True,
#         payment_type=Payment.CREDITCARD,
#         added__lte=timezone.now(),
#     )
#
#     for payment in payments:
#         payment.get_quickpaytransaction().capture()
