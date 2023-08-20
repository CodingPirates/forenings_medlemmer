from datetime import date
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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
        default=None,
        null=True,
    )
    price_in_dkk = models.DecimalField(
        "Pris", max_digits=10, decimal_places=2, default=75
    )

    def clean(self):
        errors = {}
        min_amount = 75

        if self.price_in_dkk < min_amount:
            errors[
                "price_in_dkk"
            ] = f"Prisen er for lav. Medlemskaber skal koste mindst {min_amount} kr."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.member_until = date(date.today().year, 12, 31)
        return super(Member, self).save(*args, **kwargs)
