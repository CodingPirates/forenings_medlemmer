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

    name = models.CharField("Foreningens navn", max_length=200)
    chairman = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        related_name="chairman",
        null=True,
        blank=True,
    )
    chairman_old = models.CharField("Formand", max_length=200, blank=True)
    chairman_email_old = models.EmailField("Formandens email", blank=True)
    second_chair = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="second_chair",
    )
    second_chair_old = models.CharField("Næstformand", max_length=200, blank=True)
    second_chair_email_old = models.EmailField("Næstformandens email", blank=True)
    cashier = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        related_name="cashier",
        null=True,
        blank=True,
    )
    cashier_old = models.CharField("Kasserer", max_length=200, blank=True)
    cashier_email_old = models.EmailField("Kassererens email", blank=True)
    secretary = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretary",
    )
    secretary_old = models.CharField("Sekretær", max_length=200, blank=True)
    secretary_email_old = models.EmailField("Sekretærens email", blank=True)
    union_email = models.EmailField("Foreningens email", blank=True)
    statues = models.URLField("Link til gældende vedtægter", blank=True)
    founded = models.DateField("Stiftet", blank=True, null=True)
    address = models.ForeignKey("Address", on_delete=models.PROTECT)
    board_members = models.ManyToManyField("Person", blank=True)
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

    def __str__(self):
        return "Foreningen for " + self.name

    def clean(self):
        if self.bank_main_org is False and not self.bank_account:
            raise ValidationError(
                "Vælg om foreningen har konto hos hovedforeningen. Hvis ikke skal bankkonto udfyldes."
            )
