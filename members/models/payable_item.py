import requests
import json
from django.core.mail import EmailMultiAlternatives

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from members.models import quickpaytransaction
from django.urls import reverse
from django.template.loader import get_template


def _set_quickpay_order_id():
    if settings.PAYMENT_ID_PREFIX == "prod":
        id = (
            PayableItem.objects.all().count()
            + quickpaytransaction.QuickpayTransaction.objects.all().count()
            + 1
        )
        return f"prod{'%06d' % id}"
    else:
        return f"{settings.PAYMENT_ID_PREFIX}{timezone.now().timestamp()}"


headers = {
    "accept-version": "v10",
    "content-type": "application/json",
}
auth = ("", settings.QUICKPAY_API_KEY)


class PayableItem(models.Model):
    class Meta:
        verbose_name_plural = "Betalinger"
        verbose_name = "Betaling"
        ordering = ["added"]

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
    accepted = models.BooleanField("Accepteret", default=False)
    processed = models.BooleanField("Processed", default=False)
    confirmation_sent = models.BooleanField("Bekræftelse sendt", default=False)
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
                f"{self.amount_ore} is below 1kr, rember to specify price in øre"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super(PayableItem, self).save(*args, **kwargs)

    def __create_quickpay_transaction(self):
        response = requests.post(
            settings.QUICKPAY_URL,
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
        return (
            f"Betaling: {self.person} på {self.show_amount()}kr, for {self.get_item()}"
        )

    def get_link(self, base_url=None, continue_page=None):
        if self._payment_link is not None:
            return self._payment_link

        data = {
            "amount": self.amount_ore,
            "language": "da",
            "auto_capture": True,
        }
        if base_url is not None:
            data["callback_url"] = f"{base_url}{reverse('quickpay_callback_new')}"
            data["continue_url"] = base_url
            data["continue_url"] += (
                "" if continue_page is None else reverse(continue_page)
            )
        response = requests.put(
            f"{settings.QUICKPAY_URL}/{self.quick_pay_id}/link",
            auth=auth,
            headers=headers,
            data=json.dumps(data),
        )
        if response.status_code != 200:
            raise requests.HTTPError(f"Quick pay link failed, see:\n {response.text}")
        self._payment_link = response.json()["url"]
        self.save()
        return self._payment_link

    def get_status(self):
        if self.refunded is not None:
            return "refunded"
        if self.accepted:
            return "accepted"
        response = requests.get(
            f"{settings.QUICKPAY_URL}/{self.quick_pay_id}", auth=auth, headers=headers,
        )
        if response.status_code != 200:
            raise requests.HTTPError(
                f"Quick pay get payment info failed, see:\n {response.text}"
            )
        resp = response.json()
        self.processed = resp["state"] == "processed"
        self.accepted = resp["accepted"]
        self.save()
        if self.accepted:
            return "accepted"
        else:
            return resp["state"]

    def get_item(self):
        if self.membership is not None:
            return self.membership

    def get_item_name(self):
        if self.membership is not None:
            return "Medlemsskab"

    def show_amount(self):
        return self.amount_ore / 100

    def send_payment_confirmation(self):
        if self.get_status() == "accepted" and not self.confirmation_sent:
            subject = "Betalingsbekræftelse"
            html_content, text_content = PayableItem._render_payment_confirmation(self)
            msg = EmailMultiAlternatives(
                subject, text_content, settings.DEFAULT_FROM_EMAIL, [self.person.email],
            )
            msg.attach_alternative(html_content, "text/html")
            self.confirmation_sent = True
            self.save()
            return msg.send(fail_silently=False)

    @staticmethod
    def _render_payment_confirmation(payment):
        html_template = get_template("members/email/payment_confirm.html")
        html = html_template.render({"payment": payment})

        txt_template = get_template("members/email/payment_confirm.txt")
        txt = txt_template.render({"payment": payment})

        return html, txt

    @staticmethod
    def send_all_payment_confirmations():
        return [
            payment.send_payment_confirmation()
            for payment in PayableItem.objects.filter(confirmation_sent=False)
        ]
