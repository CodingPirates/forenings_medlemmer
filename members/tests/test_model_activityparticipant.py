from django.test import TestCase
from datetime import datetime, timedelta
from members.models.person import Person
from members.models.waitinglist import WaitingList
from members.models.activityparticipant import ActivityParticipant
from django.utils import timezone

from .factories import UnionFactory
from .factories import DepartmentFactory
from .factories import FamilyFactory
from .factories import ActivityFactory
from .factories import ActivityParticipantFactory


class TestModelActivityParticipant(TestCase):
    # ToDo: Maybe test payment
    def setUp(self):
        self.union = UnionFactory()
        self.department = DepartmentFactory(union=self.union)

        self.activity = ActivityFactory(
            start_date=datetime.now(),
            end_date=datetime.now()
            + timedelta(days=365),  # Has to be long enough to be a season
            department=self.department,
            union=self.union,
        )
        self.activity.save()
        self.assertTrue(self.activity.is_season())  # If this fail increase the end_date

        self.family = FamilyFactory()
        self.family.save()

        self.person = Person(family=self.family)
        self.person.save()

        waitinglist = WaitingList(
            person=self.person,
            department=self.department,
            on_waiting_list_since=datetime.now() - timedelta(days=1),
        )
        waitinglist.save()
        self.waitinglist_id = waitinglist.id

    def test_save_waiting_list(self):
        self.participant = ActivityParticipant(
            note="test_save_waiting_list", activity=self.activity, person=self.person
        )
        self.participant.save()
        self.assertFalse(WaitingList.objects.filter(pk=self.waitinglist_id).exists())

    def test_utc_to_local_ymdhm(self):
        # test of : Get local current timestamp (t1_local) and convert to utc (t1_utc)
        # then call the utc_to_local_ymdhm(t1_utc) and check it's as expected local time
        ap = ActivityParticipantFactory()
        ymdhm = "%Y-%m-%d %H:%M"
        time_input_utc = timezone.now()
        time_expected_local = timezone.localtime(time_input_utc).strftime(ymdhm)
        time_result_local = ap.utc_to_local_ymdhm(time_input_utc)
        self.assertEqual(time_result_local, time_expected_local)
