#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from .activity import Activity

import datetime

# more stat ideas: age, region distribution
class DailyStatisticsDepartment(models.Model):
    timestamp = models.DateTimeField("Kørsels tidspunkt")
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    active_activities = models.IntegerField("Aktiviteter der er igang")
    activities = models.IntegerField("Aktiviteter i alt")
    current_activity_participants = models.IntegerField("Deltagere på aktiviteter")
    activity_participants = models.IntegerField("Deltagere på aktiviteter over al tid")
    members = models.IntegerField("Medlemmer")
    waitinglist = models.IntegerField("Venteliste")
    waitingtime = models.DurationField("Ventetid")
    payments = models.IntegerField("Betalinger")
    volunteers_male = models.IntegerField("Frivillige Mænd")
    volunteers_female = models.IntegerField("Frivillige Kvinder")
    volunteers = models.IntegerField("Frivillige")

    def save(self, *args, **kwargs):
        self.timestamp = timezone.now()

        # Get values
        active_activies = Activity.objects.filter(
            department=self.department,
            start_date__lte=self.timestamp,
            end_date__gte=self.timestamp,
        )
        activities = Activity.objects.filter(department=self.department)
        self.active_activities = len(active_activies)
        self.activities = len(activities)

        self.current_activity_participants = 1
        self.activity_participants = 1
        self.members = 1
        self.waitinglist = 1
        self.waitingtime = datetime.timedelta(days=20, hours=10)
        self.payments = 1
        self.volunteers_male = 1
        self.volunteers_female = 1
        self.volunteers = 1

        super(DailyStatisticsDepartment, self).save(*args, **kwargs)


# from members.models import DailyStatisticsDepartment
# from members.models import Department
# dep = Department.objects.all()[0]
