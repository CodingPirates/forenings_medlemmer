from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from members.admin.person_admin import PersonAdmin
from members.models import AdminUserInformation, EmailItem, Person, Volunteer
from members.tests.factories import ActivityFactory, DepartmentFactory, PersonFactory


class TestPersonAdmin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = PersonAdmin(Person, admin.site)
        self.person = PersonFactory(address_invalid=True)
        self.other_person = PersonFactory(address_invalid=True)
        self.user = get_user_model().objects.create_user(
            username="person-admin",
            password="password",
            is_staff=True,
        )
        self.superuser = get_user_model().objects.create_user(
            username="person-superuser",
            password="password",
            is_staff=True,
            is_superuser=True,
        )
        self.department = DepartmentFactory(closed_dtm=None)
        self.activity = ActivityFactory(department=self.department)
        self.admin_info = AdminUserInformation.objects.create(user=self.user)
        self.admin_info.departments.add(self.department)

    def make_request(self, user):
        request = self.factory.get("/admin/members/person/")
        request.user = user
        return request

    def make_post_request(self, user, params=None):
        request = self.factory.post("/admin/members/person/", params or {})
        request.user = user
        setattr(request, "session", self.client.session)
        setattr(request, "_messages", FallbackStorage(request))
        return request

    def test_contact_sharing_fields_are_in_consent_fieldset(self):
        fieldsets = self.admin.get_fieldsets(
            self.make_request(self.user),
            self.person,
        )

        contact_fields = fieldsets[0][1]["fields"]
        consent_fields = fieldsets[-1][1]["fields"]

        self.assertNotIn("allow_contact_from_cpdk", contact_fields)
        self.assertNotIn("allow_contact_from_other", contact_fields)
        self.assertIn("allow_contact_from_cpdk", consent_fields)
        self.assertIn("allow_contact_from_other", consent_fields)

    def test_contact_sharing_fields_are_readonly_for_superuser(self):
        readonly_fields = self.admin.get_readonly_fields(
            self.make_request(self.superuser),
            self.person,
        )

        self.assertIn("allow_contact_from_cpdk", readonly_fields)
        self.assertIn("allow_contact_from_other", readonly_fields)

    def test_create_volunteer_action_requires_single_person(self):
        request = self.make_post_request(self.user)

        response = self.admin.create_volunteer_action(
            request,
            Person.objects.filter(pk__in=[self.person.pk, self.other_person.pk]),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Volunteer.objects.filter(person=self.person).exists())
        self.assertFalse(Volunteer.objects.filter(person=self.other_person).exists())

    def test_create_volunteer_action_creates_volunteer(self):
        request = self.make_post_request(
            self.user,
            {
                "action": "create_volunteer_action",
                "department": self.department.pk,
                "activity": self.activity.pk,
                "start_date": "2026-06-07",
                "end_date": "2026-06-30",
                "_selected_action": [self.person.pk],
            },
        )

        response = self.admin.create_volunteer_action(
            request,
            Person.objects.filter(pk=self.person.pk),
        )

        self.assertEqual(response.status_code, 302)

        volunteer = Volunteer.objects.get(person=self.person)
        self.assertEqual(volunteer.department, self.department)
        self.assertEqual(volunteer.activity, self.activity)
        self.assertEqual(str(volunteer.start_date), "2026-06-07")
        self.assertEqual(str(volunteer.end_date), "2026-06-30")
        self.assertEqual(
            volunteer.user_confirmation_status,
            Volunteer.UserConfirmationStatus.WAITING_FOR_USER,
        )
        self.assertTrue(
            EmailItem.objects.filter(
                receiver=self.person.email,
                person=self.person,
            ).exists()
        )

    def test_create_volunteer_action_rejects_end_date_before_start_date(self):
        request = self.make_post_request(
            self.user,
            {
                "action": "create_volunteer_action",
                "department": self.department.pk,
                "activity": "",
                "start_date": "2026-06-30",
                "end_date": "2026-06-07",
                "_selected_action": [self.person.pk],
            },
        )

        response = self.admin.create_volunteer_action(
            request,
            Person.objects.filter(pk=self.person.pk),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Slutdato må ikke være før startdato.")
        self.assertFalse(Volunteer.objects.filter(person=self.person).exists())

    def test_create_volunteer_action_refreshes_activities_for_selected_department(self):
        other_department = DepartmentFactory(closed_dtm=None)
        self.admin_info.departments.add(other_department)
        visible_activity = ActivityFactory(
            department=self.department,
            name="Visible activity",
        )
        hidden_activity = ActivityFactory(
            department=other_department,
            name="Hidden activity",
        )

        request = self.make_post_request(
            self.user,
            {
                "action": "create_volunteer_action",
                "department": self.department.pk,
                "activity": "",
                "start_date": "2026-06-07",
                "end_date": "",
                "refresh_activity_choices": "1",
                "_selected_action": [self.person.pk],
            },
        )

        response = self.admin.create_volunteer_action(
            request,
            Person.objects.filter(pk=self.person.pk),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"[{visible_activity.start_date:%Y-%m-%d} - {visible_activity.end_date:%Y-%m-%d}] {visible_activity.name}",
        )
        self.assertNotContains(response, hidden_activity.name)
        self.assertContains(response, "⏳ Henter aktiviteter fra databasen ...")
