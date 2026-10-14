import os
from unittest import mock

from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from members.admin.volunteerrequestitem_admin import VolunteerRequestItemAdmin
from members.forms import LoggedInVolunteerRequestForm
from members.models import AuthLog, Volunteer, VolunteerRequest, VolunteerRequestItem
from members.tests.factories import DepartmentFactory, PersonFactory, VolunteerFactory


@override_settings(
    MESSAGE_STORAGE="django.contrib.messages.storage.cookie.CookieStorage"
)
class TestVolunteerSignupView(TestCase):
    def setUp(self):
        cache.clear()
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

    def test_anonymous_volunteer_request_requires_and_saves_consent(self):
        self.client.logout()
        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "name": "Nyt frivillig",
                "email": "volunteer@example.com",
                "phone": "12345678",
                "info_reference": "LinkedIn",
                "info_whishes": "Jeg vil gerne hjælpe med undervisning.",
                "departments": [self.department.pk],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Du skal give samtykke til opbevaring af dine oplysninger"
        )
        self.assertNotIn("volunteer_form_data", self.client.session)

        response = self.client.post(
            reverse("volunteer_signup"),
            {
                "name": "Nyt frivillig",
                "email": "volunteer@example.com",
                "phone": "12345678",
                "info_reference": "LinkedIn",
                "info_whishes": "Jeg vil gerne hjælpe med undervisning.",
                "departments": [self.department.pk],
                "consent": "on",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "volunteer@example.com")

        session = self.client.session
        self.assertTrue(session["volunteer_form_data"]["consent"])
        response = self.client.post(
            reverse("volunteer_signup"),
            {"verification_code": session["volunteer_verification_code"]},
        )

        self.assertEqual(response.status_code, 200)
        volunteer_request = VolunteerRequest.objects.get(email="volunteer@example.com")
        self.assertTrue(volunteer_request.consent)

    def _start_anonymous_request(self, email):
        self.client.logout()
        return self.client.post(
            reverse("volunteer_signup"),
            {
                "name": "Nogen",
                "email": email,
                "phone": "12345678",
                "info_reference": "LinkedIn",
                "info_whishes": "Jeg vil gerne hjælpe.",
                "departments": [self.department.pk],
                "consent": "on",
            },
        )

    def test_anonymous_request_with_existing_account_logs_in_after_code(self):
        user = self.person.user
        user.username = "existing@example.com"
        user.is_staff = False
        user.is_superuser = False
        user.save()

        response = self._start_anonymous_request("Existing@Example.com")
        self.assertContains(response, "verification_code")
        self.assertNotIn("_auth_user_id", self.client.session)

        response = self.client.post(
            reverse("volunteer_signup"),
            {"verification_code": self.client.session["volunteer_verification_code"]},
        )

        self.assertRedirects(response, reverse("volunteer_signup"))
        self.assertEqual(self.client.session["_auth_user_id"], str(self.person.user.pk))
        volunteer_request = VolunteerRequest.objects.get(person=self.person)
        self.assertTrue(volunteer_request.consent)
        self.assertEqual(volunteer_request.volunteerrequestitem_set.count(), 1)

        overview = self.client.get(reverse("volunteer_signup"))
        self.assertContains(overview, "Seneste Anmodninger")
        self.assertContains(overview, self.department.name)

    def test_wrong_code_never_logs_in_and_is_limited(self):
        user = self.person.user
        user.username = "existing@example.com"
        user.is_staff = False
        user.is_superuser = False
        user.save()
        self._start_anonymous_request("existing@example.com")
        real_code = self.client.session["volunteer_verification_code"]
        wrong_code = "000000" if real_code != "000000" else "111111"

        for _ in range(4):
            response = self.client.post(
                reverse("volunteer_signup"), {"verification_code": wrong_code}
            )
            self.assertContains(response, "Forkert verifikationskode")

        response = self.client.post(
            reverse("volunteer_signup"), {"verification_code": wrong_code}
        )
        self.assertContains(response, "Vent 15 minutter")

        # The flow is reset: the old code is dead and a new one must be requested
        self.assertNotIn("volunteer_verification_code", self.client.session)
        self.assertNotIn("volunteer_form_data", self.client.session)
        self.client.post(reverse("volunteer_signup"), {"verification_code": real_code})
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(VolunteerRequest.objects.filter(person=self.person).exists())

        # A fresh session for the same email is still locked, and no code is sent
        response = self._start_anonymous_request("Existing@example.com")
        self.assertContains(response, "Vent 15 minutter")
        self.assertNotIn("volunteer_verification_code", self.client.session)

        # After the lockout expires the email can try again
        cache.clear()
        self._start_anonymous_request("existing@example.com")
        response = self.client.post(
            reverse("volunteer_signup"),
            {"verification_code": self.client.session["volunteer_verification_code"]},
        )
        self.assertRedirects(response, reverse("volunteer_signup"))

    def test_authlog_cannot_be_changed_or_deleted_in_admin(self):
        user = self.person.user
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.client.force_login(user)
        entry = AuthLog.objects.create(event="login_ok", success=True)

        model_admin = admin.site._registry[AuthLog]
        request = self.factory.get("/")
        request.user = user
        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request, entry))
        self.assertFalse(model_admin.has_delete_permission(request, entry))

        response = self.client.post(
            reverse("admin:members_authlog_delete", args=[entry.pk]), {"post": "yes"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(AuthLog.objects.filter(pk=entry.pk).exists())

    def test_authlog_is_listed_under_auth_in_admin_menu(self):
        user = self.person.user
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.client.force_login(user)

        response = self.client.get(reverse("admin:index"))

        apps = {a["app_label"]: a for a in response.context["app_list"]}
        self.assertIn("AuthLog", [m["object_name"] for m in apps["auth"]["models"]])
        self.assertNotIn(
            "AuthLog", [m["object_name"] for m in apps["members"]["models"]]
        )

    @mock.patch.dict(os.environ, {"VOLUNTEER_EMAIL_VERIFICATION_CODE": "001337"})
    def test_env_test_code_does_not_work_after_lockout(self):
        self._start_anonymous_request("existing@example.com")
        for _ in range(5):
            self.client.post(
                reverse("volunteer_signup"), {"verification_code": "999999"}
            )

        self.client.post(reverse("volunteer_signup"), {"verification_code": "001337"})

        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(
            VolunteerRequest.objects.filter(email="existing@example.com").exists()
        )

    @mock.patch.dict(os.environ, {"VOLUNTEER_EMAIL_VERIFICATION_CODE": ""})
    def test_auth_events_are_logged(self):
        user = self.person.user
        user.username = "existing@example.com"
        user.set_password("secret-pw")
        user.save()
        self.client.logout()
        AuthLog.objects.all().delete()

        with self.assertLogs("members.auth", level="INFO") as logs:
            self.client.post(
                reverse("person_login"),
                {"username": "existing@example.com", "password": "wrong"},
            )
            self.client.post(
                reverse("person_login"),
                {"username": "existing@example.com", "password": "secret-pw"},
            )
            self.client.logout()
            self._start_anonymous_request("existing@example.com")
            self.client.post(
                reverse("volunteer_signup"), {"verification_code": "000000"}
            )
            self.client.post(
                reverse("volunteer_signup"),
                {
                    "verification_code": self.client.session[
                        "volunteer_verification_code"
                    ]
                },
            )

        output = "\n".join(logs.output)
        self.assertIn(
            "Login fejlet method=password identifier=existing@example.com", output
        )
        self.assertIn(
            "Login OK method=password identifier=existing@example.com", output
        )
        self.assertIn(
            "Forkert kode method=email-code identifier=existing@example.com", output
        )
        self.assertIn(
            "Login OK method=email-code identifier=existing@example.com", output
        )

        entries = list(
            AuthLog.objects.order_by("id").values_list("event", "method", "success")
        )
        self.assertEqual(
            entries,
            [
                ("login_failed", "password", False),
                ("login_ok", "password", True),
                ("code_failed", "email-code", False),
                ("login_ok", "email-code", True),
            ],
        )
        self.assertEqual(
            AuthLog.objects.filter(event="login_ok", user=self.person.user).count(), 2
        )
        self.assertNotIn("wrong", output)
        self.assertNotIn("secret-pw", output)

    @mock.patch.dict(os.environ, {"VOLUNTEER_EMAIL_VERIFICATION_CODE": "001337"})
    def test_env_test_code_logs_in_existing_user(self):
        user = self.person.user
        user.username = "existing@example.com"
        user.save()
        self._start_anonymous_request("existing@example.com")

        self.client.post(reverse("volunteer_signup"), {"verification_code": "001337"})

        self.assertEqual(self.client.session["_auth_user_id"], str(self.person.user.pk))
        self.assertTrue(VolunteerRequest.objects.filter(person=self.person).exists())

    @mock.patch.dict(os.environ, {"VOLUNTEER_EMAIL_VERIFICATION_CODE": "001337"})
    def test_login_matches_account_email_when_username_differs(self):
        user = self.person.user
        user.username = "root"
        user.email = "root@root.root"
        user.save()
        self._start_anonymous_request("root@root.root")

        self.client.post(reverse("volunteer_signup"), {"verification_code": "001337"})

        self.assertEqual(self.client.session["_auth_user_id"], str(self.person.user.pk))
        self.assertTrue(VolunteerRequest.objects.filter(person=self.person).exists())

    @mock.patch.dict(os.environ, {"VOLUNTEER_EMAIL_VERIFICATION_CODE": ""})
    def test_expired_code_is_rejected(self):
        self._start_anonymous_request("expired@example.com")
        session = self.client.session
        code = session["volunteer_verification_code"]
        session["volunteer_verification_code_sent_at"] -= 31 * 60
        session.save()

        response = self.client.post(
            reverse("volunteer_signup"), {"verification_code": code}
        )
        self.assertContains(response, "Koden er udløbet")
        self.assertFalse(
            VolunteerRequest.objects.filter(email="expired@example.com").exists()
        )

    @mock.patch.dict(os.environ, {"VOLUNTEER_EMAIL_VERIFICATION_CODE": ""})
    def test_code_within_30_minutes_is_accepted(self):
        self._start_anonymous_request("fresh@example.com")
        session = self.client.session
        code = session["volunteer_verification_code"]
        session["volunteer_verification_code_sent_at"] -= 29 * 60
        session.save()

        self.client.post(reverse("volunteer_signup"), {"verification_code": code})
        self.assertTrue(
            VolunteerRequest.objects.filter(email="fresh@example.com").exists()
        )

    def test_staff_and_superuser_are_redirected_to_login_but_request_is_linked(self):
        for flag in ("is_staff", "is_superuser"):
            with self.subTest(flag=flag):
                VolunteerRequestItem.objects.all().delete()
                VolunteerRequest.objects.all().delete()
                user = self.person.user
                user.username = "staff@example.com"
                user.is_staff = flag == "is_staff"
                user.is_superuser = flag == "is_superuser"
                user.save()
                self._start_anonymous_request("staff@example.com")

                response = self.client.post(
                    reverse("volunteer_signup"),
                    {
                        "verification_code": self.client.session[
                            "volunteer_verification_code"
                        ]
                    },
                )

                self.assertRedirects(
                    response,
                    reverse("person_login") + "?next=" + reverse("volunteer_signup"),
                )
                self.assertNotIn("_auth_user_id", self.client.session)
                self.assertTrue(
                    VolunteerRequest.objects.filter(person=self.person).exists()
                )

    def test_anonymous_volunteer_form_links_to_privacy_policy(self):
        self.client.logout()
        response = self.client.get(reverse("volunteer_signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/consent/"')
        self.assertContains(response, 'name="consent"')

    def test_cancel_pending_request_requires_confirmation(self):
        volunteer_request = VolunteerRequest.objects.create(
            person=self.person,
            info_reference="LinkedIn",
            info_whishes="Jeg vil gerne hjælpe.",
        )
        item = VolunteerRequestItem.objects.create(
            volunteer_request=volunteer_request, department=self.department
        )
        url = reverse("volunteer_request_cancel", args=[item.pk])

        overview = self.client.get(reverse("volunteer_signup"))
        self.assertContains(overview, url)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Annullér anmodning?")
        item.refresh_from_db()
        self.assertEqual(item.status, "NEW")

        response = self.client.post(url)
        self.assertRedirects(response, reverse("volunteer_signup"))
        item.refresh_from_db()
        self.assertEqual(item.status, "NOT_INTERESTED")
        self.assertIsNotNone(item.finished)

    def test_cannot_cancel_other_familys_or_processed_request(self):
        other_person = PersonFactory(address_invalid=True)
        other_request = VolunteerRequest.objects.create(
            person=other_person, info_reference="x", info_whishes="y"
        )
        other_item = VolunteerRequestItem.objects.create(
            volunteer_request=other_request, department=self.department
        )
        response = self.client.post(
            reverse("volunteer_request_cancel", args=[other_item.pk])
        )
        self.assertEqual(response.status_code, 403)
        other_item.refresh_from_db()
        self.assertEqual(other_item.status, "NEW")

        own_request = VolunteerRequest.objects.create(
            person=self.person, info_reference="x", info_whishes="y"
        )
        active_item = VolunteerRequestItem.objects.create(
            volunteer_request=own_request,
            department=self.department,
            status="ACTIVE",
        )
        response = self.client.post(
            reverse("volunteer_request_cancel", args=[active_item.pk])
        )
        self.assertEqual(response.status_code, 403)
        active_item.refresh_from_db()
        self.assertEqual(active_item.status, "ACTIVE")

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
        self.assertContains(response, "Anmodninger der afventer din godkendelse")
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

    def test_recent_requests_show_status_from_volunteerrequestitem(self):
        volunteer_request = VolunteerRequest.objects.create(
            person=self.person,
            allow_contact_from_cpdk=True,
            allow_contact_from_other=False,
            info_reference="LinkedIn",
            info_whishes="Jeg vil gerne hjælpe.",
        )
        VolunteerRequestItem.objects.create(
            volunteer_request=volunteer_request,
            department=self.department,
            status="CLOSED",
            finished=timezone.now(),
        )

        response = self.client.get(reverse("volunteer_signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Afdeling er lukket")
