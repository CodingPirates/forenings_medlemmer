from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models.emailtemplate import EmailTemplate

from .factories import (
    ActivityFactory,
    DepartmentFactory,
    FamilyFactory,
    PersonFactory,
    UnionFactory,
)


class TestCronJobSendActivityInviteReminders(TestCase):
    """Exercise cron_job_send_activityinvite_reminders: eligible invites get reminder_sent_at."""

    def setUp(self):
        self.today = timezone.now().date()
        self.union = UnionFactory()
        self.department = DepartmentFactory(union=self.union)
        self.activity = ActivityFactory(
            start_date=self.today,
            end_date=self.today + timedelta(days=365),
            min_age=5,
            max_age=17,
            department=self.department,
        )
        self.activity.save()

        EmailTemplate.objects.create(
            idname="ACT_INVITE",
            name="Activity invite",
            description="Test template",
            from_address="invite@example.com",
            subject="Invitation",
            body_html="",
            body_text="",
        )

    def _person(self):
        return PersonFactory(
            family=FamilyFactory(),
            birthday=self.today - timedelta(days=365 * 10),
        )

    def _add_invite(self, person, **kwargs):
        fields = {
            "activity": self.activity,
            "person": person,
            "invite_dtm": self.today - timedelta(days=5),
            "expire_dtm": self.today + timedelta(days=2),
        }
        fields.update(kwargs)
        ActivityInvite.objects.bulk_create([ActivityInvite(**fields)])
        return ActivityInvite.objects.get(activity=self.activity, person=person)

    def test_reminder_sent_at_set_after_cron(self):
        invite = self._add_invite(self._person())
        self.assertIsNone(invite.reminder_sent_at)

        call_command("cron_job_send_activityinvite_reminders")

        invite.refresh_from_db()
        self.assertEqual(invite.reminder_sent_at, timezone.now().date())

    def test_no_reminder_when_more_than_three_days_until_expiry(self):
        invite = self._add_invite(
            self._person(),
            expire_dtm=self.today + timedelta(days=5),
        )
        self.assertIsNone(invite.reminder_sent_at)

        call_command("cron_job_send_activityinvite_reminders")

        invite.refresh_from_db()
        self.assertIsNone(invite.reminder_sent_at)

    def test_no_reminder_when_already_reminded(self):
        invite = self._add_invite(
            self._person(),
            reminder_sent_at=self.today - timedelta(days=1),
        )
        self.assertIsNotNone(invite.reminder_sent_at)

        call_command("cron_job_send_activityinvite_reminders")

        invite.refresh_from_db()
        self.assertEqual(invite.reminder_sent_at, self.today - timedelta(days=1))

    def test_no_reminder_when_invitation_rejected(self):
        invite = self._add_invite(
            self._person(),
            rejected_at=self.today,
        )
        self.assertIsNone(invite.reminder_sent_at)

        call_command("cron_job_send_activityinvite_reminders")

        invite.refresh_from_db()
        self.assertIsNone(invite.reminder_sent_at)

    def test_no_reminder_when_person_already_signed_up(self):
        person = self._person()
        invite = self._add_invite(person)
        ActivityParticipant.objects.create(
            activity=self.activity,
            person=person,
            photo_permission=ActivityParticipant.PHOTO_OK,
        )
        self.assertIsNone(invite.reminder_sent_at)

        call_command("cron_job_send_activityinvite_reminders")

        invite.refresh_from_db()
        self.assertIsNone(invite.reminder_sent_at)
