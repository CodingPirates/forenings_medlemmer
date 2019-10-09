import datetime
from random import randint
import factory.random
from django.test import TestCase
from members.models.statistics import DepartmentStatistics
from members.tests.factories import (
    DepartmentFactory,
    ActivityFactory,
    UnionFactory,
    ActivityParticipantFactory,
)
from forenings_medlemmer.settings import TIME_ZONE


class TestDepartmentStatistics(TestCase):
    def setUp(self):
        self.departments = []
        for i in range(10):
            dep = {"department": DepartmentFactory()}
            dep["nrActivities"] = randint(1, 30)
            dep["isActive"] = [randint(0, 1) == 1 for _ in range(dep["nrActivities"])]
            dep["nrActive"] = sum(dep["isActive"])
            dep["nr_participants"] = randint(0, 100)
            dep["activities"] = [
                ActivityFactory(
                    department=dep["department"],
                    union=dep["department"].union,
                    active=active,
                )
                for active in dep["isActive"]
            ]
            dep["nr_active_participants"] = 0
            dep["nr_members"] = 0
            dep["participants"] = []
            for i in range(dep["nr_participants"]):
                activityIndex = randint(0, dep["nrActivities"] - 1)
                dep["participants"].append(
                    ActivityParticipantFactory(
                        activity=dep["activities"][activityIndex]
                    )
                )
                if dep["isActive"][activityIndex]:
                    dep["nr_active_participants"] += 1

                if dep["activities"][activityIndex].member_justified:
                    dep["nr_members"] += 1

            self.departments.append(dep)

    def test_stats_creation(self):
        for department in self.departments:
            stats = DepartmentStatistics.objects.create(
                department=department["department"]
            )
        self.assertEqual(
            stats.department, department["department"], "Departments does not match"
        )
        self.assertTrue(
            stats.timestamp - datetime.datetime.now(stats.timestamp.tzinfo)
            < datetime.timedelta(seconds=3),
            "Timestamp does not match",
        )
        self.assertEqual(
            len(department["activities"]),
            stats.activities,
            "The total number of activites does not match",
        )
        self.assertEqual(
            department["nrActive"],
            stats.active_activities,
            "The number of active activites does not match",
        )
        self.assertEqual(
            department["nr_participants"],
            stats.activity_participants,
            "The number of total participants does not match",
        )
        self.assertEqual(
            department["nr_active_participants"],
            stats.current_activity_participants,
            "The number of active participants does not match",
        )
        self.assertEqual(
            department["nr_members"],
            stats.members,
            "The number of members does not match",
        )

        self.fail("Finish implementation and test!")
