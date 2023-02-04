#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from members.models.zipcoderegion import ZipcodeRegion
from django.utils import timezone


class DailyStatisticsRegion(models.Model):
    timestamp = models.DateTimeField(
        "Kørsels tidspunkt", null=False, blank=False, default=timezone.now
    )
    region = models.CharField(
        "Region",
        blank=False,
        null=False,
        max_length=4,
        choices=ZipcodeRegion.REGION_CHOICES,
    )
    departments = models.IntegerField("Afdelinger", null=False, blank=False, default=0)
    active_activities = models.IntegerField(
        "Aktiviteter der er igang", null=False, blank=False, default=0
    )
    activities = models.IntegerField(
        "Aktiviteter i alt", null=False, blank=False, default=0
    )
    current_activity_participants = models.IntegerField(
        "Deltagere på aktiviteter", null=False, blank=False, default=0
    )
    activity_participants = models.IntegerField(
        "Deltagere på aktiviteter over al tid", null=False, blank=False, default=0
    )
    members = models.IntegerField("Medlemmer", null=False, blank=False, default=0)
    waitinglist = models.IntegerField("Venteliste", null=False, blank=False, default=0)
    payments = models.IntegerField("Betalinger", null=False, blank=False, default=0)
    volunteers_male = models.IntegerField(
        "Frivillige Mænd", null=False, blank=False, default=0
    )
    volunteers_female = models.IntegerField(
        "Frivillige Kvinder", null=False, blank=False, default=0
    )
    volunteers = models.IntegerField("Frivillige", null=False, blank=False, default=0)
