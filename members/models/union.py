#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone


class Union(models.Model):
    class Meta:
        verbose_name = "Forening"
        verbose_name_plural = "Foreninger"
        ordering = ["name"]
        permissions = (
            ("view_all_unions", "Can view all Foreninger"),
            ("show_ledger_account", "Show General Ledger Account"),
            ("show_new_membership_model", "Show New Membership Model"),
        )

    help_union = """Vi tilføjer automatisk "Coding Pirates" foran navnet når vi nævner det de fleste steder på siden."""
    name = models.CharField("Foreningens navn", max_length=200, help_text=help_union)

    chairman = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        related_name="chairman",
        null=True,
        blank=True,
        verbose_name="Formand",
    )
    chairman_old = models.CharField("Formand", max_length=200, blank=True)
    chairman_email_old = models.EmailField("Formandens email", blank=True)
    second_chair = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="second_chair",
        verbose_name="Næstformand",
    )
    second_chair_old = models.CharField("Næstformand", max_length=200, blank=True)
    second_chair_email_old = models.EmailField("Næstformandens email", blank=True)
    cashier = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        related_name="cashier",
        null=True,
        blank=True,
        verbose_name="Kasserer",
    )
    cashier_old = models.CharField("Kasserer", max_length=200, blank=True)
    cashier_email_old = models.EmailField("Kassererens email", blank=True)
    secretary = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretary",
        verbose_name="Sekretær",
    )
    secretary_old = models.CharField("Sekretær", max_length=200, blank=True)
    secretary_email_old = models.EmailField("Sekretærens email", blank=True)
    email = models.EmailField("Foreningens email", blank=True)
    statues = models.URLField("Link til gældende vedtægter", blank=True)
    founded_at = models.DateField("Stiftet", blank=True, null=True)
    closed_at = models.DateField(
        "Lukket",
        blank=True,
        null=True,
        default=None,
        help_text="Dato for lukning af denne forening",
    )
    memberships_allowed_at = models.DateField(
        "Dato hvor medlemskaber er tilladt fra",
        help_text="Hvis feltet er tomt, vil det ikke være tilladt at være medlem af foreningen.",
        default=timezone.now,
        blank=True,
        null=True,
    )
    address = models.ForeignKey(
        "Address", on_delete=models.PROTECT, verbose_name="Adresse"
    )
    board_members = models.ManyToManyField(
        "Person", blank=True, verbose_name="Menige medlemmer"
    )
    board_members_old = models.TextField("Menige medlemmer", blank=True)
    help_text = f"Medlemskabet skal koste minimum {settings.MINIMUM_MEMBERSHIP_PRICE_IN_DKK} kr. pga. Dansk Ungdoms Fællesråds medlemsdefinition."
    membership_price_in_dkk = models.DecimalField(
        "Kontingent",
        max_digits=10,
        decimal_places=2,
        default=settings.MINIMUM_MEMBERSHIP_PRICE_IN_DKK,
        help_text=help_text,
    )
    new_membership_model_activated_at = models.DateTimeField(
        "Ny medlemskabsmodel aktiveret",
        blank=True,
        null=True,
        help_text="Bemærk: Aktiverer du den nye medlemstabel for en forening kan det ikke ændres tilbage! Det har betydning for flere ting, og vi låser derfor feltet. Står der ikke en dato i feltet, er den nye model ikke aktiv. Står der en dato i fremtiden er den heller ikke aktiv endnu, og kan ændres. Står der en dato i fortiden er den aktiv fra og med den dato.",
    )
    bank_main_org = models.BooleanField(
        "Sæt kryds hvis I har konto hos hovedforeningen (og ikke har egen bankkonto).",
        default=True,
    )
    bank_account = models.CharField(
        "Bankkonto:",
        max_length=15,
        blank=True,
        help_text="Kontonummer i formatet 1234-1234567890",
        validators=[
            RegexValidator(
                regex="^[0-9]{4} *?-? *?[0-9]{6,10} *?$",
                message="Indtast kontonummer i det rigtige format.",
            )
        ],
    )
    gl_account = models.CharField(
        "Finanskonto:",
        max_length=4,
        blank=True,
        help_text="Kontonummer i formatet 1234",
        validators=[
            RegexValidator(
                regex="^[0-9]{4}",
                message="Indtast kontonummer i det rigtige format.",
            )
        ],
    )
    cvr = models.CharField(
        "CVR-nummer",
        max_length=8,
        blank=True,
        help_text="CVR-nummer i formatet 12345678",
        validators=[
            RegexValidator(
                regex="^[0-9]{8}$",
                message="Indtast CVR-nummer i det rigtige format.",
            )
        ],
    )

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}
        min_amount = settings.MINIMUM_MEMBERSHIP_PRICE_IN_DKK

        if self.membership_price_in_dkk < min_amount:
            errors["membership_price_in_dkk"] = (
                f"Prisen er for lav. Medlemskaber skal koste mindst {min_amount} kr."
            )

        if errors:
            raise ValidationError(errors)

        if self.bank_main_org is False and not self.bank_account:
            raise ValidationError(
                "Vælg om foreningen har konto hos hovedforeningen. Hvis ikke skal bankkonto udfyldes."
            )
