from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from members.admin.volunteerrequestitem_admin import VolunteerRequestItemAdmin
from members.forms import LoggedInVolunteerRequestForm
from members.models import Volunteer, VolunteerRequest, VolunteerRequestItem
from members.tests.factories import DepartmentFactory, PersonFactory, VolunteerFactory


@override_settings(
    MESSAGE_STORAGE="django.contrib.messages.storage.cookie.CookieStorage"
)
class TestVolunteerSignupView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.person = PersonFactory(
            address_invalid=True,
            allow_contact_from_cpdk=False,
            allow_contact_from_other=False,
        )
        self.department = DepartmentFactory(closed_dtm=None)
        self.volunteer = VolunteerFactory(
            person=self.person,
            removed=None,
        )
        self.client.force_login(self.person.user)

    def test_updates_contact_preference_and_logs_admin_history(self):
        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "form_id": "volunteer_contact_preference",
                "person_id": self.person.pk,
                "allow_contact_from_cpdk": "on",
                "allow_contact_from_other": "on",
            },
        )

        self.assertRedirects(response, reverse("volunteer_signup"))

        self.person.refresh_from_db()
        self.assertTrue(self.person.allow_contact_from_cpdk)
        self.assertTrue(self.person.allow_contact_from_other)

        log_entry = LogEntry.objects.filter(object_id=str(self.person.pk)).latest(
            "action_time"
        )
        self.assertIn(
            "Må Coding Pirates Denmark kontakte mig?",
            log_entry.get_change_message(),
        )
        self.assertIn(
            "Må andre afdelinger kontakte mig?",
            log_entry.get_change_message(),
        )

    def test_rejects_updates_for_other_familys_volunteer(self):
        other_volunteer = VolunteerFactory(
            removed=None,
            person=PersonFactory(
                address_invalid=True,
                allow_contact_from_cpdk=False,
                allow_contact_from_other=False,
            ),
        )

        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "form_id": "volunteer_contact_preference",
                "person_id": other_volunteer.person.pk,
                "allow_contact_from_cpdk": "on",
                "allow_contact_from_other": "on",
            },
        )

        self.assertEqual(response.status_code, 403)

        other_volunteer.person.refresh_from_db()
        self.assertFalse(other_volunteer.person.allow_contact_from_cpdk)
        self.assertFalse(other_volunteer.person.allow_contact_from_other)
        self.assertFalse(
            LogEntry.objects.filter(
                object_id=str(other_volunteer.person.pk),
                user=self.person.user,
            ).exists()
        )

    def test_rejects_updates_for_family_member_without_volunteer_role(self):
        other_person_in_family = PersonFactory(
            family=self.person.family,
            user=None,
            address_invalid=True,
            allow_contact_from_cpdk=False,
            allow_contact_from_other=False,
        )

        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "form_id": "volunteer_contact_preference",
                "person_id": other_person_in_family.pk,
                "allow_contact_from_cpdk": "on",
                "allow_contact_from_other": "on",
            },
        )

        self.assertEqual(response.status_code, 403)

        other_person_in_family.refresh_from_db()
        self.assertFalse(other_person_in_family.allow_contact_from_cpdk)
        self.assertFalse(other_person_in_family.allow_contact_from_other)

    def test_updates_contact_preference_for_person_with_multiple_active_volunteer_roles(
        self,
    ):
        VolunteerFactory(
            person=self.person,
            removed=None,
        )

        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "form_id": "volunteer_contact_preference",
                "person_id": self.person.pk,
                "allow_contact_from_cpdk": "on",
                "allow_contact_from_other": "on",
            },
        )

        self.assertRedirects(response, reverse("volunteer_signup"))

        self.person.refresh_from_db()
        self.assertTrue(self.person.allow_contact_from_cpdk)
        self.assertTrue(self.person.allow_contact_from_other)

    def test_logged_in_volunteer_request_saves_contact_preference(self):
        self.person.allow_contact_from_cpdk = True
        self.person.allow_contact_from_other = True
        self.person.save(
            update_fields=["allow_contact_from_cpdk", "allow_contact_from_other"]
        )

        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "person": self.person.pk,
                "info_reference": "LinkedIn",
                "info_whishes": "Jeg vil gerne hjælpe med undervisning.",
                "departments": [self.department.pk],
            },
        )

        self.assertEqual(response.status_code, 200)

        volunteer_request = VolunteerRequest.objects.get(person=self.person)
        self.assertTrue(volunteer_request.allow_contact_from_cpdk)
        self.assertTrue(volunteer_request.allow_contact_from_other)

    def test_logged_in_form_does_not_expose_contact_preference_fields(self):
        form = LoggedInVolunteerRequestForm(user=self.person.user)

        self.assertNotIn("allow_contact_from_cpdk", form.fields)
        self.assertNotIn("allow_contact_from_other", form.fields)

    def test_pending_admin_created_volunteer_is_shown_for_confirmation(self):
        pending_volunteer = VolunteerFactory(
            person=self.person,
            department=self.department,
            removed=None,
            user_confirmation_status=Volunteer.UserConfirmationStatus.WAITING_FOR_USER,
        )

        response = self.client.get(reverse("volunteer_signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Afventer din godkendelse")
        self.assertContains(
            response,
            f'name="volunteer_id" value="{pending_volunteer.pk}"',
            html=False,
        )

    def test_accept_pending_admin_created_volunteer_updates_status_and_logs(self):
        pending_volunteer = VolunteerFactory(
            person=self.person,
            department=self.department,
            removed=None,
            user_confirmation_status=Volunteer.UserConfirmationStatus.WAITING_FOR_USER,
        )

        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "form_id": "volunteer_user_confirmation",
                "volunteer_id": pending_volunteer.pk,
                "confirmation_action": "accept",
            },
        )

        self.assertRedirects(response, reverse("volunteer_signup"))

        pending_volunteer.refresh_from_db()
        self.assertEqual(
            pending_volunteer.user_confirmation_status,
            Volunteer.UserConfirmationStatus.APPROVED_BY_USER,
        )

        log_entry = LogEntry.objects.filter(object_id=str(pending_volunteer.pk)).latest(
            "action_time"
        )
        self.assertIn("Brugerbekræftelse", log_entry.get_change_message())
        self.assertIn("Godkendt af bruger", log_entry.get_change_message())

    def test_reject_pending_admin_created_volunteer_updates_status_and_logs(self):
        pending_volunteer = VolunteerFactory(
            person=self.person,
            department=self.department,
            removed=None,
            user_confirmation_status=Volunteer.UserConfirmationStatus.WAITING_FOR_USER,
        )

        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "form_id": "volunteer_user_confirmation",
                "volunteer_id": pending_volunteer.pk,
                "confirmation_action": "reject",
            },
        )

        self.assertRedirects(response, reverse("volunteer_signup"))

        pending_volunteer.refresh_from_db()
        self.assertEqual(
            pending_volunteer.user_confirmation_status,
            Volunteer.UserConfirmationStatus.REJECTED_BY_USER,
        )

        log_entry = LogEntry.objects.filter(object_id=str(pending_volunteer.pk)).latest(
            "action_time"
        )
        self.assertIn("Brugerbekræftelse", log_entry.get_change_message())
        self.assertIn("Afvist af bruger", log_entry.get_change_message())

    def test_volunteer_account_created_page_renders(self):
        response = self.client.get(reverse("volunteer_account_created"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("person_login"))

    def test_accept_request_copies_contact_preference_to_person(self):
        volunteer_request = VolunteerRequest.objects.create(
            person=self.person,
            allow_contact_from_cpdk=True,
            allow_contact_from_other=True,
            info_reference="LinkedIn",
            info_whishes="Jeg vil gerne hjælpe med undervisning.",
        )
        volunteer_request_item = VolunteerRequestItem.objects.create(
            volunteer_request=volunteer_request,
            department=self.department,
        )

        request = self.factory.post(reverse("volunteer_signup"))
        request.user = self.person.user
        request._messages = messages.storage.default_storage(request)
        admin_instance = VolunteerRequestItemAdmin(VolunteerRequestItem, admin.site)

        admin_instance.accept_request(
            request,
            VolunteerRequestItem.objects.filter(pk=volunteer_request_item.pk),
        )

        created_volunteer = Volunteer.objects.exclude(pk=self.volunteer.pk).get(
            person=self.person, department=self.department
        )
        self.person.refresh_from_db()
        self.assertEqual(created_volunteer.person_id, self.person.pk)
        self.assertTrue(self.person.allow_contact_from_cpdk)
        self.assertTrue(self.person.allow_contact_from_other)
