from datetime import datetime, timedelta

from django.test import TestCase

from members.models.activityinvite import ActivityInvite
from members.models.emailtemplate import EmailTemplate
from members.models.waitinglist import WaitingList

from .factories import (
    ActivityFactory,
    DepartmentFactory,
    PersonFactory,
    UnionFactory,
)


class TestModelActivityInvite(TestCase):
    def setUp(self):
        union = UnionFactory()
        self.department = DepartmentFactory(union=union)
        self.other_department = DepartmentFactory(union=union)
        self.activity = ActivityFactory(
            department=self.department,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=365),
        )
        self.person = PersonFactory()
        EmailTemplate.objects.create(
            idname="ACT_INVITE",
            name="Aktivitetsinvitation",
            description="Invitation til aktivitet",
            from_address="from@example.com",
            subject="Invitation",
        )

    def add_waiting_lists(self):
        activity_waiting_list = WaitingList.objects.create(
            person=self.person,
            department=self.department,
            on_waiting_list_since=datetime.now() - timedelta(days=1),
        )
        other_waiting_list = WaitingList.objects.create(
            person=self.person,
            department=self.other_department,
            on_waiting_list_since=datetime.now() - timedelta(days=1),
        )
        return activity_waiting_list, other_waiting_list

    def test_save_removes_only_activity_department_waiting_list(self):
        activity_waiting_list, other_waiting_list = self.add_waiting_lists()

        ActivityInvite.objects.create(activity=self.activity, person=self.person)

        self.assertFalse(
            WaitingList.objects.filter(pk=activity_waiting_list.pk).exists()
        )
        self.assertTrue(WaitingList.objects.filter(pk=other_waiting_list.pk).exists())

    def test_save_keeps_waiting_list_when_removal_is_disabled(self):
        self.activity.remove_from_waiting_list_on_invite = False
        self.activity.save()
        activity_waiting_list, other_waiting_list = self.add_waiting_lists()

        ActivityInvite.objects.create(activity=self.activity, person=self.person)

        self.assertTrue(
            WaitingList.objects.filter(pk=activity_waiting_list.pk).exists()
        )
        self.assertTrue(WaitingList.objects.filter(pk=other_waiting_list.pk).exists())


#             activity=self.activity,
#             person=self.person
#         )
#         self.invite.clean()
