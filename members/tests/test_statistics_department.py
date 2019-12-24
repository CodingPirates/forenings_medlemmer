import datetime
from random import randint
from django.test import TestCase
from django.utils import timezone
from members.models.statistics import (
    gatherDayliStatistics,
    DepartmentStatistics,
)

from members.tests.factories import (
    DepartmentFactory,
    ActivityFactory,
    ActivityParticipantFactory,
    WaitingListFactory,
    VolunteerFactory,
)


class TestDepartmentStatistics(TestCase):
    def setUp(self):
        self.nr_closed_Departments = randint(1, 30)
        DepartmentFactory.create_batch(self.nr_closed_Departments)

        self.nr_departments = randint(1, 30)
        departments = DepartmentFactory.create_batch(
            self.nr_departments, closed_dtm=None
        )

        self.testDepartments = []
        for department in departments:
            testDepartment = {"department": department}

            # creates activites
            testDepartment["nrActivities"] = randint(1, 30)
            testDepartment["isActive"] = [
                randint(0, 1) == 1 for _ in range(testDepartment["nrActivities"])
            ]
            testDepartment["nrActive"] = sum(testDepartment["isActive"])
            testDepartment["nr_participants"] = randint(0, 100)
            testDepartment["activities"] = [
                ActivityFactory(
                    department=testDepartment["department"],
                    union=testDepartment["department"].union,
                    active=active,
                )
                for active in testDepartment["isActive"]
            ]
            testDepartment["nr_active_participants"] = 0
            testDepartment["nr_members"] = 0
            testDepartment["participants"] = []
            for i in range(testDepartment["nr_participants"]):
                activityIndex = randint(0, testDepartment["nrActivities"] - 1)
                testDepartment["participants"].append(
                    ActivityParticipantFactory(
                        activity=testDepartment["activities"][activityIndex]
                    )
                )
                if testDepartment["isActive"][activityIndex]:
                    testDepartment["nr_active_participants"] += 1

                if testDepartment["activities"][activityIndex].member_justified:
                    testDepartment["nr_members"] += 1

            testDepartment["nr_waitinglist"] = randint(1, 100)
            waitlist = WaitingListFactory.create_batch(
                testDepartment["nr_waitinglist"],
                department=testDepartment["department"],
            )
            testDepartment["waitingtime"] = timezone.now() - min(
                [wait.on_waiting_list_since for wait in waitlist]
            )
            testDepartment["nr_volunteers"] = len(
                VolunteerFactory.create_batch(
                    randint(0, 50), department=testDepartment["department"]
                )
            )

            self.testDepartments.append(testDepartment)

    def test_stats_creation(self):
        gatherDayliStatistics()
        allStats = DepartmentStatistics.objects.all()
        self.assertEqual(len(self.testDepartments), len(allStats))
        for testDepartment in self.testDepartments:
            stats = DepartmentStatistics.objects.filter(
                department=testDepartment["department"]
            )[0]

            self.assertTrue(
                stats.timestamp - datetime.datetime.now(stats.timestamp.tzinfo)
                < datetime.timedelta(seconds=3),
                "Timestamp does not match",
            )
            self.assertEqual(
                len(testDepartment["activities"]),
                stats.activities,
                "The total number of activites does not match",
            )
            self.assertEqual(
                testDepartment["nrActive"],
                stats.active_activities,
                "The number of active activites does not match",
            )

            self.assertEqual(
                testDepartment["nr_participants"],
                stats.activity_participants,
                "The number of total participants does not match",
            )
            self.assertEqual(
                testDepartment["nr_active_participants"],
                stats.current_activity_participants,
                "The number of active participants does not match",
            )
            self.assertEqual(
                testDepartment["nr_members"],
                stats.members,
                "The number of members does not match",
            )
            self.assertEqual(
                testDepartment["nr_waitinglist"],
                stats.waitinglist,
                "The number of people on waitinglist does not match",
            )
            self.assertTrue(
                testDepartment["waitingtime"] - stats.waitingtime
                < datetime.timedelta(seconds=3)
            )
            self.assertEqual(
                testDepartment["nr_volunteers"],
                stats.volunteers,
                "The number of volunteers does not match",
            )
