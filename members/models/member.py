from datetime import date
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

import members.models.payment


def end_of_year():
    return date(date.today().year, 12, 31)


class Member(models.Model):
    class Meta:
        verbose_name = "Medlem"
        verbose_name_plural = "Medlemmer"

    union = models.ForeignKey(
        "Union", on_delete=models.PROTECT, verbose_name="Forening"
    )
    person = models.ForeignKey("Person", on_delete=models.PROTECT)
    member_since = models.DateField(
        "Medlemskab start", blank=False, default=timezone.now
    )
    member_until = models.DateField(
        "Medlemskab slut",
        blank=True,
        default=end_of_year,
        null=True,
    )
    price_in_dkk = models.DecimalField(
        "Pris",
        max_digits=10,
        decimal_places=2,
        default=settings.MINIMUM_MEMBERSHIP_PRICE_IN_DKK,
    )
    paid_at = models.DateTimeField("Betalt", blank=True, null=True)

    def __str__(self):
        return f"{self.person}, {self.union}, {self.member_since.year}"

    def clean(self):
        errors = {}
        min_amount = settings.MINIMUM_MEMBERSHIP_PRICE_IN_DKK

        if self.price_in_dkk < min_amount:
            errors["price_in_dkk"] = (
                f"Prisen er for lav. Medlemskaber skal koste mindst {min_amount} kr."
            )

        if errors:
            raise ValidationError(errors)

    def paid(self):
        # not paid if unconfirmed payments on this activity participation
        return not members.models.payment.Payment.objects.filter(
            member=self, accepted_at=None
        )

    def get_payment_link(self):
        payment = members.models.payment.Payment.objects.get(
            member=self, accepted_at=None
        )
        if payment.payment_type == members.models.payment.Payment.CREDITCARD:
            return payment.get_quickpaytransaction().get_link_url()
        else:
            return 'javascript:alert("Kan ikke betales her:  Kontakt Coding Pirates for hjælp");'
