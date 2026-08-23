from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from members.models import VolunteerRequest, VolunteerRequestItem
from members.tests.factories import (
    ActivityFactory,
    ActivityParticipantFactory,
    DepartmentFactory,
    PersonFactory,
    VolunteerFactory,
)


class TestDepartmentAdminCloseFlow(TestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            username="department-admin",
            email="department-admin@example.com",
            password="password",
        )
        self.client.force_login(self.superuser)
        PersonFactory(user=self.superuser, address_invalid=True)

        self.department = DepartmentFactory(
            name="CP Test Afdeling",
            closed_dtm=None,
            isVisible=True,
            isOpening=False,
            has_waiting_list=True,
        )

        self.open_volunteer = VolunteerFactory(
            department=self.department,
            start_date=date(2026, 1, 10),
            end_date=None,
            removed=None,
        )
        self.closed_volunteer = VolunteerFactory(
            department=self.department,
            start_date=date(2026, 1, 11),
            end_date=date(2026, 2, 1),
            removed=None,
        )

        self.url = reverse("admin:members_department_change", args=[self.department.pk])

    def _department_post_data(self, closed_dtm, extra=None):
        if isinstance(closed_dtm, str):
            closed_dtm_value = closed_dtm
        else:
            closed_dtm_value = closed_dtm.strftime("%Y-%m-%d")

        created_value = self.department.created
        if not isinstance(created_value, date):
            created_value = created_value.date()

        data = {
            "name": self.department.name,
            "union": str(self.department.union_id),
            "description": self.department.description,
            "open_hours": self.department.open_hours,
            "responsible_name": self.department.responsible_name,
            "department_email": self.department.department_email,
            "address": str(self.department.address_id),
            "website": self.department.website,
            "created": created_value.strftime("%Y-%m-%d"),
            "closed_dtm": closed_dtm_value,
            "AdminUserInformation_departments-TOTAL_FORMS": "0",
            "AdminUserInformation_departments-INITIAL_FORMS": "0",
            "AdminUserInformation_departments-MIN_NUM_FORMS": "0",
            "AdminUserInformation_departments-MAX_NUM_FORMS": "1000",
            "_save": "Gem",
        }

        if self.department.isVisible:
            data["isVisible"] = "on"
        if self.department.isOpening:
            data["isOpening"] = "on"
        if self.department.has_waiting_list:
            data["has_waiting_list"] = "on"

        if extra:
            data.update(extra)

        return data

    def test_shows_confirmation_page_when_closing_department_with_open_volunteers(self):
        response = self.client.post(
            self.url,
            data=self._department_post_data(closed_dtm="2026-08-15"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bekræft lukning af afdeling")
        self.assertContains(response, self.open_volunteer.person.name)

        self.department.refresh_from_db()
        self.open_volunteer.refresh_from_db()
        self.assertIsNone(self.department.closed_dtm)
        self.assertIsNone(self.open_volunteer.end_date)

    def test_confirmed_close_sets_department_close_date_and_open_volunteer_end_dates(
        self,
    ):
        response = self.client.post(
            self.url,
            data=self._department_post_data(
                closed_dtm="2026-08-15",
                extra={"_confirm_close_department": "1"},
            ),
        )

        self.assertIn(response.status_code, (200, 302))

        self.department.refresh_from_db()
        self.open_volunteer.refresh_from_db()
        self.closed_volunteer.refresh_from_db()

        self.assertEqual(self.department.closed_dtm, date(2026, 8, 15))
        self.assertEqual(self.open_volunteer.end_date, date(2026, 8, 15))
        self.assertEqual(self.closed_volunteer.end_date, date(2026, 2, 1))

    def test_close_without_open_volunteers_does_not_show_confirmation_step(self):
        self.open_volunteer.end_date = date(2026, 2, 2)
        self.open_volunteer.save(update_fields=["end_date"])

        response = self.client.post(
            self.url,
            data=self._department_post_data(closed_dtm="2026-08-15"),
        )

        self.assertIn(response.status_code, (200, 302))

        self.department.refresh_from_db()
        self.assertEqual(self.department.closed_dtm, date(2026, 8, 15))

    def test_shows_confirmation_page_for_unfinished_volunteer_request_items(self):
        self.open_volunteer.end_date = date(2026, 2, 2)
        self.open_volunteer.save(update_fields=["end_date"])

        volunteer_request = VolunteerRequest.objects.create(
            name="Uafsluttet Frivillig",
            email="uafsluttet@example.com",
            phone="12345678",
            info_reference="LinkedIn",
            info_whishes="Jeg vil gerne hjælpe med kodeundervisning.",
        )
        VolunteerRequestItem.objects.create(
            volunteer_request=volunteer_request,
            department=self.department,
            status="NEW",
            finished=None,
        )

        response = self.client.post(
            self.url,
            data=self._department_post_data(closed_dtm="2026-08-15"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Uafsluttede frivillig-anmodninger")
        self.assertContains(response, "uafsluttet@example.com")

        self.department.refresh_from_db()
        self.assertIsNone(self.department.closed_dtm)

    def test_confirmed_close_marks_unfinished_request_items_closed(self):
        volunteer_request = VolunteerRequest.objects.create(
            name="Afdelingslukning test",
            email="close-status@example.com",
            phone="12345678",
            info_reference="LinkedIn",
            info_whishes="Jeg vil gerne hjælpe.",
        )
        request_item = VolunteerRequestItem.objects.create(
            volunteer_request=volunteer_request,
            department=self.department,
            status="NEW",
            finished=None,
        )

        response = self.client.post(
            self.url,
            data=self._department_post_data(
                closed_dtm="2026-08-15",
                extra={"_confirm_close_department": "1"},
            ),
        )

        self.assertIn(response.status_code, (200, 302))

        request_item.refresh_from_db()
        self.assertEqual(request_item.status, "CLOSED")
        self.assertIsNotNone(request_item.finished)

    def test_close_is_blocked_if_participants_exist_on_activity_ending_after_close_date(
        self,
    ):
        self.open_volunteer.end_date = date(2026, 2, 2)
        self.open_volunteer.save(update_fields=["end_date"])

        conflicting_activity = ActivityFactory(
            department=self.department,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 9, 1),
            signup_closing=date(2026, 7, 25),
        )
        ActivityParticipantFactory(activity=conflicting_activity)

        response = self.client.post(
            self.url,
            data=self._department_post_data(
                closed_dtm="2026-08-15",
                extra={"_confirm_close_department": "1"},
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Afdelingen kan ikke lukkes, fordi der er deltagere på en aktivitet med slutdato efter afdelingens lukkedato.",
        )

        self.department.refresh_from_db()
        self.assertIsNone(self.department.closed_dtm)
