from django.test import TestCase

from .factories import ActivityFactory, PersonFactory
from collections import Counter
from faker import Faker

fake = Faker()


class TestModelActivity(TestCase):
    def setUp(self):
        self.activity = ActivityFactory(min_age=8, max_age=12)

        birthday = fake.date_time_between(
            start_date="-" + str(self.activity.max_age) + "y",
            end_date="-" + str(self.activity.min_age) + "y",
        )
        self.applicablePersons = PersonFactory.create_batch(50, birthday=birthday)

        birthday = fake.date_time_between(
            start_date="-" + str(self.activity.min_age) + "y",
            end_date="-" + str(self.activity.min_age + 10) + "y",
        )
        self.not_applicablePersons_tooYoung = PersonFactory.create_batch(
            50, birthday=birthday
        )

        birthday = fake.date_time_between(
            start_date="-" + str(self.activity.max_age + 10) + "y",
            end_date="-" + str(self.activity.max_age) + "y",
        )
        self.not_applicablePersons_tooOld = PersonFactory.create_batch(
            50, birthday=birthday
        )

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
