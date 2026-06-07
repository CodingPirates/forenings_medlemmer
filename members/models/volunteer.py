#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone


class Volunteer(models.Model):
    class Meta:
        verbose_name = "Frivillig"
        verbose_name_plural = "Frivillige"

    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    department = models.ForeignKey(
        "Department", on_delete=models.CASCADE, verbose_name="Afdeling"
    )
    activity = models.ForeignKey(
        "Activity",
        on_delete=models.CASCADE,
        verbose_name="Aktivitet",
        blank=True,
        null=True,
    )

    def has_certificate(self):
        return self.person.has_certificate

    added_at = models.DateTimeField("Start", default=timezone.now)
    confirmed = models.DateTimeField("Bekræftet", blank=True, null=True, default=None)
    removed = models.DateTimeField("Slut", blank=True, null=True, default=None)

    start_date = models.DateField("Startdato", blank=True, null=True, default=None)
    end_date = models.DateField("Slutdato", blank=True, null=True, default=None)

    info_reference = models.TextField(
        "Reference",
        help_text="Hvor har du hørt om Coding Pirates (SoMe, Facebook, Instagram, LinkedIn, en ven, en kollega, etc)?",
        max_length=200,
        blank=True,
        null=True,
    )
    info_whishes = models.TextField(
        "Ønsker",
        help_text="Hvilke ønsker har du til at være frivillig hos Coding Pirates?",
        max_length=1024,
        blank=True,
        null=True,
    )
    allow_cpdk_contact = models.BooleanField(
        "Må Coding Pirates Denmark kontakte mig?", default=False
    )

    def __str__(self):
        return self.person.__str__()
