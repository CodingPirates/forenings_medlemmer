import datetime

from django.test import TestCase
from django.utils import timezone

from members.models.statistics import (
    DepartmentStatistics,
    gatherDayliStatistics,
)
from members.tests.factories import (
    ActivityFactory,
    ActivityParticipantFactory,
    DepartmentFactory,
    VolunteerFactory,
    WaitingListFactory,
)


class TestDepartmentStatistics(TestCase):
    def setUp(self):
        self.nr_closed_Departments = 2
        DepartmentFactory.create_batch(self.nr_closed_Departments)

        self.nr_departments = 3
        departments = DepartmentFactory.create_batch(
            self.nr_departments, closed_dtm=None
        )

        self.testDepartments = []
        for department in departments:
            testDepartment = {"department": department}

            # creates activites
            testDepartment["nrActivities"] = 4
            testDepartment["isActive"] = [
                i % 2 == 0 for i in range(testDepartment["nrActivities"])
            ]
            testDepartment["nrActive"] = sum(testDepartment["isActive"])
            testDepartment["nr_participants"] = 10
            testDepartment["activities"] = [
                ActivityFactory(
                    department=testDepartment["department"],
                    active=active,
                )
                for active in testDepartment["isActive"]
            ]
            testDepartment["nr_active_participants"] = 0
            testDepartment["nr_members"] = 0
            testDepartment["participants"] = []
            for i in range(testDepartment["nr_participants"]):
                activityIndex = i % testDepartment["nrActivities"]
                testDepartment["participants"].append(
                    ActivityParticipantFactory(
                        activity=testDepartment["activities"][activityIndex]
                    )
                )
                if testDepartment["isActive"][activityIndex]:
                    testDepartment["nr_active_participants"] += 1

                if testDepartment["activities"][
                    activityIndex
                ].is_eligable_for_membership():
                    testDepartment["nr_members"] += 1

            testDepartment["nr_waitinglist"] = 5
            waitlist = WaitingListFactory.create_batch(
                testDepartment["nr_waitinglist"],
                department=testDepartment["department"],
            )
            testDepartment["waitingtime"] = timezone.now() - min(
                [wait.on_waiting_list_since for wait in waitlist]
            )
            testDepartment["nr_volunteers"] = len(
                VolunteerFactory.create_batch(
                    3, department=testDepartment["department"]
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
