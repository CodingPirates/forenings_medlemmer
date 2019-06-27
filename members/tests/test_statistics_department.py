from django.test import TestCase
from members.models import DailyStatisticsDepartment
from members.tests.factories import DepartmentFactory, ActivityFactory, UnionFactory
from django.utils import timezone
import datetime
from random import randint


class TestModelDepartment(TestCase):
    def setUp(self):
        self.nrActivities = randint(0, 30)
        print(ActivityFactory())
        [print(ActivityFactory().department) for _ in range(30)]

        # self.activities = [ActivityFactory() for _ in range(30)]
        # self.department = DepartmentFactory()
        # Creates two activities, one that is active and one that isn't

    def test_stats_creation(self):
        # stats = DailyStatisticsDepartment(department=self.department)

        timestamp = timezone.now()
        # stats.save()

        # Check that department is corret.
        # self.assertEqual(stats.department, self.department)
        # self.assertEqual(stats.activities, self.nrActivities)
        # self.assertLess(stats.timestamp - timestamp, datetime.timedelta(seconds=2))

        # print(stats)
