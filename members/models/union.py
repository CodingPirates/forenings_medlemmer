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
    chairman = models.CharField("Formand", max_length=200, blank=True)
    chairman_email = models.EmailField("Formandens email", blank=True)
    second_chair = models.CharField("Næstformand", max_length=200, blank=True)
    second_chair_email = models.EmailField("Næstformandens email", blank=True)
    cashier = models.CharField("Kasserer", max_length=200, blank=True)
    cashier_email = models.EmailField("Kassererens email", blank=True)
    secretary = models.CharField("Sekretær", max_length=200, blank=True)
    secratary_email = models.EmailField("Sekretærens email", blank=True)
    union_email = models.EmailField("Foreningens email", blank=True)
    statues = models.URLField("Link til gældende vedtægter", blank=True)
    founded = models.DateField("Stiftet", blank=True, null=True)
    regions = (("S", "Sjælland"), ("J", "Jylland"), ("F", "Fyn"), ("Ø", "Øer"))
    region = models.CharField("region", max_length=1, choices=regions)

    placename = models.CharField("Stednavn", max_length=200, blank=True)
    zipcode = models.CharField("Postnummer", max_length=10)
    city = models.CharField("By", max_length=200)
    streetname = models.CharField("Vejnavn", max_length=200)
    housenumber = models.CharField("Husnummer", max_length=10)
    floor = models.CharField("Etage", max_length=10, blank=True)
    door = models.CharField("Dør", max_length=10, blank=True)
    boardMembers = models.TextField("Menige medlemmer", blank=True)
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
