#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from ..activity import Activity
from ..activityparticipant import ActivityParticipant

import datetime

# more stat ideas: age, region distribution
class DepartmentStatistics(models.Model):
    timestamp = models.DateTimeField("Kørsels tidspunkt")
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    active_activities = models.IntegerField("Aktiviteter der er igang")
    activities = models.IntegerField("Aktiviteter i alt")
    current_activity_participants = models.IntegerField(
        "Samlet antal deltagere på aktive aktiviteter"
    )
    activity_participants = models.IntegerField(
        "Samlet antal deltage på alle aktiviteter"
    )
    members = models.IntegerField("Antal medlemmer")
    waitinglist = models.IntegerField("Antal på venteliste")
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

        self.activity_participants = sum(
            [
                len(ActivityParticipant.objects.filter(activity=activity))
                for activity in activities
            ]
        )
        self.current_activity_participants = sum(
            [
                len(ActivityParticipant.objects.filter(activity=activity))
                for activity in active_activies
            ]
        )
        activities_members = [
            activity for activity in activities if activity.member_justified
        ]
        self.members = sum(
            [
                len(ActivityParticipant.objects.filter(activity=activity))
                for activity in activities
            ]
        )

        # TODO Finish these
        self.waitinglist = 1
        self.waitingtime = datetime.timedelta(days=20, hours=10)
        self.payments = 1
        self.volunteers_male = 1
        self.volunteers_female = 1
        self.volunteers = 1

        super(DepartmentStatistics, self).save(*args, **kwargs)
