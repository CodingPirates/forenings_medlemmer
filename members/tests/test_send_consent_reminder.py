from datetime import datetime, timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time

from members.models.emailitem import EmailItem
from members.models.emailtemplate import EmailTemplate
from members.models.person import Person
from members.tests.factories import PaymentFactory, PersonFactory
from members.tests.factories.factory_helpers import TIMEZONE


class TestSendConsentReminderCommand(TestCase):
    """Tests for ``send_consent_reminder`` management command."""

    ref_now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=TIMEZONE)

    def setUp(self):
        EmailTemplate.objects.create(
            idname="CONSENT_REMINDER",
            name="Consent reminder",
            description="Test",
            from_address="noreply@example.com",
            subject="Reminder subject",
            body_html="<p>html</p>",
            body_text="text",
        )

    def _old_eligible_person(self):
        # Person created on 2022-01-01, with no attached user,
        # i.e. eligible for consent reminder by age and inactivity
        with freeze_time(datetime(2022, 1, 1, tzinfo=TIMEZONE)):
            return PersonFactory(user=None)

    def test_dry_run_lists_family_without_updating_timestamps(self):
        person = self._old_eligible_person()
        stdout = StringIO()
        with freeze_time(self.ref_now):
            call_command("send_consent_reminder", "--dry-run", stdout=stdout)
        person.refresh_from_db()

        # verify that running in dry-run mode does not update the timestamp
        self.assertIsNone(person.consent_reminder_sent_at)

        # verify that the family is listed in the output
        out = stdout.getvalue()
        self.assertIn("Would send", out)
        self.assertIn(f"#{person.family.id}", out)
        self.assertIn("Done.", out)

        # verify that no email was actually sent
        self.assertEqual(0, EmailItem.objects.count())

    @override_settings(SITE_CONTACT="TEST <from@example.com>", BASE_URL="http://test/")
    def test_sends_and_sets_consent_reminder_sent_at(self):
        # arrange
        person = self._old_eligible_person()

        # act
        stdout = StringIO()
        with freeze_time(self.ref_now):
            call_command("send_consent_reminder", stdout=stdout)

        # assert
        person.refresh_from_db()
        self.assertIsNotNone(person.consent_reminder_sent_at)
        self.assertIn(
            f"Sending consent reminder to family #{person.family.id}", stdout.getvalue()
        )
        self.assertEqual(1, EmailItem.objects.count())

        # verify that the timestamp was updated
        self.assertIsNotNone(person.consent_reminder_sent_at)
        self.assertIn("Done. Families: 1, persons marked: 1", stdout.getvalue())
        self.assertEqual(1, EmailItem.objects.count())

    def test_skips_person_added_too_recently(self):
        # arrange
        with freeze_time(datetime(2024, 1, 1, tzinfo=TIMEZONE)):
            person = PersonFactory(user=None)

        # act
        stdout = StringIO()
        with freeze_time(self.ref_now):
            call_command("send_consent_reminder", stdout=stdout)

        # assert
        person.refresh_from_db()
        self.assertIsNone(person.consent_reminder_sent_at)
        self.assertIn("Done. Families: 0, persons marked: 0", stdout.getvalue())

    def test_skips_when_reminder_sent_within_last_year(self):
        # arrange
        person = self._old_eligible_person()

        # act
        stdout = StringIO()
        with freeze_time(self.ref_now):
            previous_sent = timezone.now() - timedelta(days=180)
            person.consent_reminder_sent_at = previous_sent
            person.save()
            call_command("send_consent_reminder", stdout=stdout)

        # assert
        person.refresh_from_db()
        self.assertEqual(person.consent_reminder_sent_at, previous_sent)
        self.assertIn("Done. Families: 0, persons marked: 0", stdout.getvalue())

    def test_skips_family_opted_out_of_mail(self):
        # arrange
        person = self._old_eligible_person()
        person.family.dont_send_mails = True
        person.family.save()

        # act
        stdout = StringIO()
        with freeze_time(self.ref_now):
            call_command("send_consent_reminder", stdout=stdout)

        # assert
        person.refresh_from_db()
        self.assertIsNone(person.consent_reminder_sent_at)
        self.assertIn("Done. Families: 0, persons marked: 0", stdout.getvalue())

    def test_skips_anonymized_family(self):
        # arrange
        person = self._old_eligible_person()
        person.family.anonymized = True
        person.family.save()

        # act
        stdout = StringIO()
        with freeze_time(self.ref_now):
            call_command("send_consent_reminder", stdout=stdout)

        # assert
        person.refresh_from_db()
        self.assertIsNone(person.consent_reminder_sent_at)
        self.assertIn("Done. Families: 0, persons marked: 0", stdout.getvalue())

    def test_skips_person_with_recent_family_payment(self):
        # arrange
        person = self._old_eligible_person()

        # act
        stdout = StringIO()
        with freeze_time(self.ref_now):
            PaymentFactory(
                person=person,
                family=person.family,
                added_at=timezone.make_aware(datetime(2024, 6, 1, 12, 0, 0)),
            )
            call_command("send_consent_reminder", stdout=stdout)

        # assert
        person.refresh_from_db()
        self.assertIsNone(person.consent_reminder_sent_at)
        self.assertIn("Done. Families: 0, persons marked: 0", stdout.getvalue())

    @override_settings(SITE_CONTACT="TEST <from@example.com>", BASE_URL="http://test/")
    def test_one_email_per_family_marks_all_eligible_persons(self):
        # arrange
        with freeze_time(datetime(2022, 1, 1, tzinfo=TIMEZONE)):
            p1 = PersonFactory(user=None)
            family = p1.family
            PersonFactory(user=None, family=family)

        # act
        stdout = StringIO()
        with freeze_time(self.ref_now):
            call_command("send_consent_reminder", stdout=stdout)

        # assert
        self.assertIn("Done. Families: 1, persons marked: 2", stdout.getvalue())
        self.assertEqual(1, EmailItem.objects.count())
        self.assertEqual(
            2,
            Person.objects.filter(
                family=family, consent_reminder_sent_at__isnull=False
            ).count(),
        )
