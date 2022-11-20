from django.test import TestCase
from members.models.waitinglist import WaitingList
from members.tests.factories import (
    WaitingListFactory,
    DepartmentFactory,
    PersonFactory,
)
from members.tests.factories.factory_helpers import TIMEZONE
from freezegun import freeze_time
from datetime import datetime, timedelta
import faker


class TestModelWaitinglist(TestCase):
    def test_people_are_added_to_waiting_list_in_signup_order(self):
        department = DepartmentFactory()
        subscription0 = WaitingListFactory(department=department)
        with freeze_time(datetime.now() + timedelta(seconds=60)):
            subscription1 = WaitingListFactory(department=department)
        with freeze_time(datetime.now() + timedelta(seconds=120)):
            subscription2 = WaitingListFactory(department=department)

        subscriptions = WaitingList.objects.all()

        self.assertEqual(3, subscriptions.count())
        self.assertEqual(subscription0, subscriptions[0])
        self.assertEqual(subscription1, subscriptions[1])
        self.assertEqual(subscription2, subscriptions[2])

    def test_waiting_list_is_sorted_by_person_signup_date(self):
        department = DepartmentFactory()
        subscription0 = WaitingListFactory(
            person__added_at=datetime(2017, 1, 1, tzinfo=TIMEZONE),
            department=department,
        )
        subscription1 = WaitingListFactory(
            person__added_at=datetime(2015, 1, 1, tzinfo=TIMEZONE),
            department=department,
        )
        subscription2 = WaitingListFactory(
            person__added_at=datetime(2019, 1, 1, tzinfo=TIMEZONE),
            department=department,
        )

        subscriptions = WaitingList.objects.all()

        self.assertEqual(3, subscriptions.count())
        self.assertEqual(subscription1, subscriptions[0])
        self.assertEqual(subscription0, subscriptions[1])
        self.assertEqual(subscription2, subscriptions[2])

    def test_position_on_waitinglist_computed_correctly(self):
        department = DepartmentFactory()
        subscription0 = WaitingListFactory(
            department=department,
            person__added_at=datetime(2017, 1, 1, tzinfo=TIMEZONE),
        )
        self.assertEqual(1, subscription0.number_on_waiting_list())
        subscription1 = WaitingListFactory(
            department=department,
            person__added_at=datetime(2015, 1, 1, tzinfo=TIMEZONE),
        )
        self.assertEqual(2, subscription0.number_on_waiting_list())
        self.assertEqual(1, subscription1.number_on_waiting_list())

    def test_different_waitinglists_does_not_interfere(self):
        department0 = DepartmentFactory()
        department1 = DepartmentFactory()
        person = PersonFactory()
        subscription0 = WaitingListFactory(person=person, department=department0)
        subscription1 = WaitingListFactory(person=person, department=department1)

        self.assertEqual(1, subscription0.number_on_waiting_list())
        self.assertEqual(1, subscription1.number_on_waiting_list())

        fake = faker.Faker()

        # Add a lot of people with random sign-up dates to the second
        # list.
        # NB. fake.date_time() only returns past datetimes, thus all
        # subscriptions will be added infront of our new person, not
        # after
        n = 30
        for i in range(n):
            WaitingListFactory(
                person__added_at=fake.date_time(tzinfo=TIMEZONE), department=department1
            )

        # Should not interfere with position on the first list
        self.assertEqual(1, subscription0.number_on_waiting_list())

        # We are placed last on the second waiting list
        self.assertEqual(n + 1, subscription1.number_on_waiting_list())

    def test_get_by_child(self):
        departments = [DepartmentFactory(), DepartmentFactory()]
        persons = [PersonFactory(), PersonFactory()]

        # Not on wainting list yet
        self.assertEqual(len(WaitingList.get_by_child(persons[0])), 0)

        # Sign up for waiting LIst
        WaitingListFactory(person=persons[0], department=departments[0])
        WaitingListFactory(person=persons[1], department=departments[0])

        self.assertEqual(WaitingList.get_by_child(persons[0]), [(departments[0], 1)])
        self.assertEqual(WaitingList.get_by_child(persons[1]), [(departments[0], 2)])

        # Sign up for more
        WaitingListFactory(person=persons[1], department=departments[1])
        WaitingListFactory(person=persons[0], department=departments[1])

        # Checks for Ordering
        self.assertEqual(
            WaitingList.get_by_child(persons[0]),
            [(departments[0], 1), (departments[1], 1)],
        )
        self.assertEqual(
            WaitingList.get_by_child(persons[1]),
            [(departments[0], 2), (departments[1], 2)],
        )
