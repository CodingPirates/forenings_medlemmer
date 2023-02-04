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

    def has_certificate(self):
        return self.person.has_certificate

    added_at = models.DateTimeField("Start", default=timezone.now)
    confirmed = models.DateTimeField("Bekræftet", blank=True, null=True, default=None)
    removed = models.DateTimeField("Slut", blank=True, null=True, default=None)

    def __str__(self):
        return self.person.__str__()
