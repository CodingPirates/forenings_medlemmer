#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models


class EquipmentLoan(models.Model):
    class Meta:
        verbose_name = "Udstyrs udlån"
        verbose_name_plural = "Udstyrs udlån"

    equipment = models.ForeignKey(
        "Equipment", blank=False, null=False, on_delete=models.CASCADE
    )
    count = models.IntegerField(
        "Antal enheder udlånt", default=1, blank=False, null=False
    )
    loaned_dtm = models.DateField("Udlånt", auto_now_add=True, null=False, blank=False)
    expected_back_dtm = models.DateField("Forventet returneret", null=True, blank=True)
    returned_dtm = models.DateField("Afleveret", null=True, blank=True)
    person = models.ForeignKey(
        "Person", blank=False, null=False, on_delete=models.CASCADE
    )
    department = models.ForeignKey(
        "Department", blank=False, null=False, on_delete=models.CASCADE
    )
    note = models.TextField("Noter", null=True, blank=True)

    def __str__(self):
        return (
            self.equipment.title
            + " er lånt ud til "
            + self.person.name
            + " - "
            + self.department.name
        )
