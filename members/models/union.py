#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class Union(models.Model):
    class Meta:
        verbose_name_plural = "Foreninger"
        verbose_name = "Forening"
        ordering = ["name"]
        permissions = (
            ("view_all_unions", "Can view all Foreninger"),
            ("show_ledger_account", "Show General Ledger Account"),
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
    address = models.ForeignKey(
        "Address", on_delete=models.PROTECT, verbose_name="Adresse"
    )
    board_members = models.ManyToManyField(
        "Person", blank=True, verbose_name="Menige medlemmer"
    )
    board_members_old = models.TextField("Menige medlemmer", blank=True)
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

    def __str__(self):
        return self.name

    def clean(self):
        if self.bank_main_org is False and not self.bank_account:
            raise ValidationError(
                "Vælg om foreningen har konto hos hovedforeningen. Hvis ikke skal bankkonto udfyldes."
            )
