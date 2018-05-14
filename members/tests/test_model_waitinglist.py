from django.test import TestCase
from members.models.union import Union
from members.models.department import Department
from members.models.family import Family
from members.models.person import Person
from members.models.waitinglist import WaitingList
from freezegun import freeze_time
from datetime import datetime, timedelta


class TestModelWaitinglist(TestCase):
    def setUp(self):
        self.union = Union()
        self.union.save()

        self.department = Department(
            union=self.union
        )
        self.department.save()

        self.family = Family()
        self.family.save()

        self.person1 = Person(
            family=self.family
        )
        self.person1.save()
        self.person1_waitinglist = WaitingList(
            person=self.person1,
            department=self.department
        )
        self.person1_waitinglist.save()

        # Artifically wait 60 seconds with adding person2 to the waitinglist
        with freeze_time(datetime.now() + timedelta(seconds=60)):
            self.person2 = Person(
                family=self.family
            )
            self.person2.save()
            self.person2_waitinglist = WaitingList(
                person=self.person2,
                department=self.department
            )
            self.person2_waitinglist.save()

    def test_waiting_list_position(self):
        self.assertEqual(self.person1_waitinglist.number_on_waiting_list(), 1)
        self.assertEqual(self.person2_waitinglist.number_on_waiting_list(), 2)
