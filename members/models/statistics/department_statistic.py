#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

from members.models import ActivityParticipant, Activity, Department
import datetime


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

        # TODO Finish these
        self.waitinglist = 1
        self.waitingtime = datetime.timedelta(days=20, hours=10)
        self.payments = 1
        self.volunteers_male = 1
        self.volunteers_female = 1
        self.volunteers = 1
        super(DepartmentStatistics, self).save(*args, **kwargs)

    @staticmethod
    def gatherStatistics(timestamp):
        print(len(Department.objects.filter(closed_dtm=None)))
        [
            DepartmentStatistics.objects.create(
                department=department, timestamp=timestamp
            )
            for department in Department.objects.filter(closed_dtm=None)
        ]


# OLD WAY
# for department in departments:
#     dailyStatisticsDepartment = (
#         members.models.dailystatisticsdepartment.DailyStatisticsDepartment()
#     )
#
#     dailyStatisticsDepartment.members = 0  # TODO: to loosely defined now
#     dailyStatisticsDepartment.waitinglist = (
#         Person.objects.filter(waitinglist__department=department)
#         .distinct()
#         .count()
#     )
#     firstWaitingListItem = (
#         WaitingList.objects.filter(department=department)
#         .order_by("on_waiting_list_since")
#         .first()
#     )
#     if firstWaitingListItem:
#         dailyStatisticsDepartment.waitingtime = (
#             timestamp - firstWaitingListItem.on_waiting_list_since
#         )
#     else:
#         dailyStatisticsDepartment.waitingtime = datetime.timedelta(days=0)
#     dailyStatisticsDepartment.payments = Payment.objects.filter(
#         activity__department=department,
#         refunded_dtm=None,
#         confirmed_dtm__isnull=False,
#     ).aggregate(sum=Coalesce(Sum("amount_ore"), 0))["sum"]
#     dailyStatisticsDepartment.volunteers_male = (
#         Person.objects.filter(
#             volunteer__department=department, gender=Person.MALE
#         )
#         .distinct()
#         .count()
#     )
#     dailyStatisticsDepartment.volunteers_female = (
#         Person.objects.filter(
#             volunteer__department=department, gender=Person.FEMALE
#         )
#         .distinct()
#         .count()
#     )
#     dailyStatisticsDepartment.volunteers = (
#         dailyStatisticsDepartment.volunteers_male
#         + dailyStatisticsDepartment.volunteers_female
#     )
