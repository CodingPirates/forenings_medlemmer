#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone


class DailyStatisticsGeneral(models.Model):
    timestamp = models.DateTimeField(
        "Kørsels tidspunkt", null=False, blank=False, default=timezone.now
    )
    persons = models.IntegerField("Personer", null=False, blank=False, default=0)
    children_male = models.IntegerField(
        "Børn Drenge", null=False, blank=False, default=0
    )
    children_female = models.IntegerField(
        "Børn Piger", null=False, blank=False, default=0
    )
    children = models.IntegerField("Børn", null=False, blank=False, default=0)
    volunteers_male = models.IntegerField(
        "Frivillige Mænd", null=False, blank=False, default=0
    )
    volunteers_female = models.IntegerField(
        "Frivillige Kvinder", null=False, blank=False, default=0
    )
    volunteers = models.IntegerField("Frivillige", null=False, blank=False, default=0)
    departments = models.IntegerField("Afdelinger", null=False, blank=False, default=0)
    unions = models.IntegerField("Lokalforeninger", null=False, blank=False, default=0)
    waitinglist_male = models.IntegerField(
        "Drenge på venteliste", null=False, blank=False, default=0
    )
    waitinglist_female = models.IntegerField(
        "Piger på venteliste", null=False, blank=False, default=0
    )
    waitinglist = models.IntegerField(
        "Personer på venteliste", null=False, blank=False, default=0
    )
    family_visits = models.IntegerField(
        "Profilsider besøgt foregående 24 timer", null=False, blank=False, default=0
    )
    dead_profiles = models.IntegerField(
        "Profilsider efterladt over et år", null=False, blank=False, default=0
    )
    current_activity_participants = models.IntegerField(
        "Deltagere på aktiviteter", null=False, blank=False, default=0
    )
    activity_participants = models.IntegerField(
        "Deltagere på aktiviteter over al tid", null=False, blank=False, default=0
    )
    activity_participants_male = models.IntegerField(
        "Deltagere på aktiviteter over al tid (drenge)",
        null=False,
        blank=False,
        default=0,
    )
    activity_participants_female = models.IntegerField(
        "Deltagere på aktiviteter over al tid (piger)",
        null=False,
        blank=False,
        default=0,
    )
    payments = models.IntegerField("Betalinger sum", null=False, blank=False, default=0)
    payments_transactions = models.IntegerField(
        "Betalinger transaktioner", null=False, blank=False, default=0
    )
