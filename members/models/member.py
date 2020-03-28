#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone


class Member(models.Model):
    class Meta:
        verbose_name = "Medlem"
        verbose_name_plural = "Medlemmer"
        ordering = ["is_active", "member_since"]

    department = models.ForeignKey("Department", on_delete=models.PROTECT)
    person = models.OneToOneField("Person", on_delete=models.PROTECT)
    is_active = models.BooleanField("Aktiv", default=True)
    member_since = models.DateField("Indmeldt", blank=False, default=timezone.now)
    member_until = models.DateField("Udmeldt", blank=True, default=None, null=True)

    def name(self):
        return "{}".format(self.person)

    name.short_description = "Navn"

    def __str__(self):
        return "{}, {}".format(self.person, self.department)
