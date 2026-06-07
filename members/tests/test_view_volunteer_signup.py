from django.contrib.admin.models import LogEntry
from django.test import TestCase
from django.urls import reverse

from members.tests.factories import PersonFactory, VolunteerFactory


class TestVolunteerSignupView(TestCase):
    def setUp(self):
        self.person = PersonFactory(address_invalid=True)
        self.volunteer = VolunteerFactory(
            person=self.person,
            allow_cpdk_contact=False,
            removed=None,
        )
        self.client.force_login(self.person.user)

    def test_updates_contact_preference_and_logs_admin_history(self):
        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "form_id": "volunteer_contact_preference",
                "volunteer_id": self.volunteer.pk,
                "allow_cpdk_contact": "on",
            },
        )

        self.assertRedirects(response, reverse("volunteer_signup"))

        self.volunteer.refresh_from_db()
        self.assertTrue(self.volunteer.allow_cpdk_contact)

        log_entry = LogEntry.objects.filter(object_id=str(self.volunteer.pk)).latest(
            "action_time"
        )
        self.assertIn(
            "Må Coding Pirates Denmark kontakte mig?",
            log_entry.get_change_message(),
        )

    def test_rejects_updates_for_other_familys_volunteer(self):
        other_volunteer = VolunteerFactory(allow_cpdk_contact=False, removed=None)

        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "form_id": "volunteer_contact_preference",
                "volunteer_id": other_volunteer.pk,
                "allow_cpdk_contact": "on",
            },
        )

        self.assertEqual(response.status_code, 403)

        other_volunteer.refresh_from_db()
        self.assertFalse(other_volunteer.allow_cpdk_contact)
        self.assertFalse(
            LogEntry.objects.filter(
                object_id=str(other_volunteer.pk),
                user=self.person.user,
            ).exists()
        )
