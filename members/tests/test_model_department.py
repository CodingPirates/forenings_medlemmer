from datetime import timedelta
from random import randint
from django.test import TestCase
from django.utils import timezone
from members.models import Department
from .factories import DepartmentFactory, ActivityFactory


class TestModelDepartment(TestCase):
    def test_get_open_departments(self):
        open_departments = DepartmentFactory.create_batch(10, closed_dtm=None)
        [
            ActivityFactory.create(
                start_date=timezone.now(),
                end_date=timezone.now() - timedelta(days=randint(0, 350)),
                department=department,
            )
            for department in open_departments
        ]
        # Department young than a year and no activities
        new_departments = DepartmentFactory.create_batch(
            10,
            closed_dtm=None,
            created=timezone.now() - timedelta(days=randint(0, 350)),
        )
        expected = set(open_departments + new_departments)

        # Closed departments
        DepartmentFactory.create_batch(10, closed_dtm=timezone.now())

        # depatments older than a year not closed but no activities in the
        # last year or nor activites at all
        old_departments = DepartmentFactory.create_batch(
            10,
            closed_dtm=None,
            created=timezone.now() - timedelta(days=randint(367, 999)),
        )
        [
            ActivityFactory.create(
                end_date=timezone.now() - timedelta(days=randint(367, 999)),
                department=department,
            )
            for department in old_departments[:5]
        ]

        self.assertEqual(expected, set(Department.get_open_departments()))
