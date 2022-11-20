#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import Coalesce
from datetime import timedelta

from members.models import (
    ActivityParticipant,
    Activity,
    Department,
    WaitingList,
    Payment,
    Volunteer,
    Person,
)


class DepartmentStatistics(models.Model):
    # more stat ideas: age, region distribution
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
        if self.timestamp is None:
            self.timestamp = timezone.now()
        active_activies = Activity.objects.filter(
            department=self.department,
            start_date__lte=self.timestamp,
            end_date__gte=self.timestamp,
        )
        activities = Activity.objects.filter(department=self.department)
        self.active_activities = active_activies.count()
        self.activities = activities.count()

        self.activity_participants = sum(
            [
                ActivityParticipant.objects.filter(activity=activity).count()
                for activity in activities
            ]
        )
        self.current_activity_participants = sum(
            [
                ActivityParticipant.objects.filter(activity=activity).distinct().count()
                for activity in active_activies
            ]
        )
        activities_members = [
            activity for activity in activities if activity.member_justified
        ]
        self.members = sum(
            [
                ActivityParticipant.objects.filter(activity=activity).distinct().count()
                for activity in activities_members
            ]
        )

        waitinglist = WaitingList.objects.filter(department=self.department).distinct()

        self.waitinglist = waitinglist.count()

        self.waitingtime = (
            max([timezone.now() - wait.on_waiting_list_since for wait in waitinglist])
            if len(waitinglist) > 0
            else timedelta(0)
        )
        self.volunteers = Volunteer.objects.filter(department=self.department).count()

        # TODO The three fields below does not have tests since we need to change
        # paymetns and gender soon anyways
        self.volunteers_male = (
            Person.objects.filter(
                volunteer__department=self.department, gender=Person.MALE
            )
            .distinct()
            .count()
        )
        self.volunteers_female = (
            Person.objects.filter(
                volunteer__department=self.department, gender=Person.FEMALE
            )
            .distinct()
            .count()
        )

        self.payments = Payment.objects.filter(
            activity__department=self.department,
            refunded_at=None,
            confirmed_at__isnull=False,
        ).aggregate(sum=Coalesce(Sum("amount_ore"), 0))["sum"]

        super(DepartmentStatistics, self).save(*args, **kwargs)

    @staticmethod
    def gatherStatistics(timestamp):
        [
            DepartmentStatistics.objects.create(
                department=department, timestamp=timestamp
            )
            for department in Department.objects.filter(closed_dtm=None)
        ]
