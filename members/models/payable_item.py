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
    refunded = models.DateTimeField("Refunderet", null=True, blank=True)
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
    processed = models.BooleanField("Processed", default=False)
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
                    "continue_url": continue_url,
                }
            ),
        )
        if response.status_code != 200:
            raise requests.HTTPError(f"Quick pay link failed, see:\n {response.text}")
        self._payment_link = response.json()["url"]
        return self._payment_link

    def get_status(self):
        # Only call quickpay api if not done or refunded
        if self.refunded is not None:
            return "refunded"
        if self.processed:
            return self.state

        response = requests.get(
            f"{url}/{self.quick_pay_id}", auth=auth, headers=headers,
        )
        if response.status_code != 200:
            raise requests.HTTPError(
                f"Quick pay get payment info failed, see:\n {response.text}"
            )
        state = response.json()["state"]
        if state == "processed":
            self.processed = True
            self.save()
        return state

    def get_type_name(self):
        if self.membership is not None:
            return self.membership

    def show_amount(self):
        return self.amount_ore / 100
