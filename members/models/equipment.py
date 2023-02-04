#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError


class Equipment(models.Model):
    class Meta:
        verbose_name = "Udstyr"
        verbose_name_plural = "Udstyr"

    created_dtm = models.DateTimeField("Oprettet", auto_now_add=True)
    title = models.CharField("Titel", max_length=200, blank=False, null=False)
    brand = models.CharField(
        "Mærke", max_length=200, blank=True, null=True, default=None
    )
    model = models.CharField(
        "Model", max_length=200, blank=True, null=True, default=None
    )
    serial = models.CharField(
        "Serienummer", max_length=200, blank=True, null=True, default=None
    )

    count = models.IntegerField("Antal enheder", default=1, blank=False, null=False)
    link = models.URLField("Link til mere info", blank=True)
    notes = models.TextField("Generelle noter", blank=True)
    buy_price = models.DecimalField(
        "Købs pris", max_digits=10, decimal_places=2, blank=True, null=True
    )
    buy_place = models.TextField("Købs sted", null=True, blank=True)
    buy_date = models.DateField("Købs dato", null=True, blank=True)
    department = models.ForeignKey(
        "Department", blank=True, null=True, on_delete=models.CASCADE
    )
    union = models.ForeignKey("Union", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def clean(self):
        # Make sure equipment is owned by someone
        if self.department is None and self.union is None:
            raise ValidationError("Udfyld ejer afdeling, forening eller begge")
        if self.department is not None and self.union is not None:
            if self.department.union != self.union:
                raise ValidationError(
                    "Afdelingen der er valgt er ikke i den valgte forening"
                )

    def save(self, *args, **kwargs):
        if self.union is None:
            self.union = self.department.union
        return super(Equipment, self).save(*args, **kwargs)
