from django.test import TestCase

from .factories import ActivityFactory, PersonFactory
from collections import Counter
from faker import Faker

fake = Faker()


class TestModelActivity(TestCase):
    def setUp(self):
        self.activity = ActivityFactory(min_age=8, max_age=12)

        self.applicablePersons = [
            PersonFactory(
                birthday=fake.date_between(
                    start_date="-"
                    + str(int((self.activity.max_age + 1) * 365.24 - 1))
                    + "d",
                    end_date="-" + str(self.activity.min_age) + "y",
                )
            )
            for i in range(0, 50)
        ]

        print("-" + str(int((self.activity.max_age + 1) * 365.24 - 1)) + "d")
        print("-" + str(self.activity.min_age) + "y")

        self.not_applicablePersons_tooYoung = [
            PersonFactory(
                birthday=fake.date_time_between(
                    start_date="-" + str(int(self.activity.min_age * 365.24 + 1)) + "d",
                    end_date="+2y",  # str(-(self.activity.min_age - 10)) + "y",
                ),
            )
            for i in range(0, 50)
        ]

        print("-" + str(int(self.activity.min_age * 365.24 + 1)) + "d")
        print("+2y",)

        self.not_applicablePersons_tooOld = [
            PersonFactory(
                birthday=fake.date_time_between(
                    start_date="-" + str(self.activity.max_age + 10) + "y",
                    end_date="-" + str(int((self.activity.max_age + 1) * 365.24)) + "d",
                ),
            )
            for i in range(0, 50)
        ]

    # Modified from django.test.testcases.TransactionTestCase.assertQuerysetEqual
    def assertQuerysetDiffernt(
        self, qs, values, transform=repr, ordered=True, msg=None
    ):
        items = map(transform, qs)
        if not ordered:
            return self.assertNotEqual(Counter(items), Counter(values), msg=msg)

    def test_get_applicable_persons_dynamic(self):
        self.assertQuerysetEqual(
            self.applicablePersons,
            self.activity.get_applicable_persons(),
            transform=lambda x: x,
            ordered=False,
        )
        self.assertQuerysetDiffernt(
            self.not_applicablePersons_tooYoung,
            self.activity.get_applicable_persons(),
            transform=lambda x: x,
            ordered=False,
        )
        self.assertQuerysetDiffernt(
            self.not_applicablePersons_tooOld,
            self.activity.get_applicable_persons(),
            transform=lambda x: x,
            ordered=False,
        )
