import csv
from datetime import date, datetime, timezone
from io import StringIO
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import translation

from members.admin.member_admin import (
    MemberAdmin,
    MemberSummaryExportForm,
    generate_member_csv,
)
from members.models import AdminUserInformation, Member, Payment

from .factories import MemberFactory, PersonFactory, UnionFactory


class MemberAdminPaymentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        PersonFactory(user=self.user)
        self.client.force_login(self.user)
        self.url = reverse("admin:members_member_changelist")
        self.paid = MemberFactory()
        self.unpaid = MemberFactory()
        self.no_payment = MemberFactory()
        self.earlier = datetime(2024, 1, 1, 12, tzinfo=timezone.utc)
        self.latest = datetime(2024, 2, 1, 12, tzinfo=timezone.utc)
        for confirmed_at in (self.earlier, self.latest, None):
            Payment.objects.create(
                member=self.paid,
                family=self.paid.person.family,
                body_text="Medlemskab",
                confirmed_at=confirmed_at,
            )
        Payment.objects.create(
            member=self.unpaid,
            family=self.unpaid.person.family,
            body_text="Medlemskab",
            accepted_at=self.earlier,
        )

    def test_payment_filter_and_latest_date(self):
        for parameters, expected in (
            ({}, {self.paid.pk}),
            ({"payment_status": "yes"}, {self.paid.pk}),
            ({"payment_status": "no"}, {self.unpaid.pk, self.no_payment.pk}),
            (
                {"payment_status": "all"},
                {self.paid.pk, self.unpaid.pk, self.no_payment.pk},
            ),
        ):
            with self.subTest(parameters=parameters):
                response = self.client.get(self.url, parameters)
                self.assertEqual(response.status_code, 200)
                results = list(response.context["cl"].result_list)
                self.assertEqual({member.pk for member in results}, expected)
                self.assertEqual(len(results), len(expected))
                if self.paid.pk in expected:
                    paid = next(
                        member for member in results if member.pk == self.paid.pk
                    )
                    self.assertEqual(paid.latest_payment_confirmed_at, self.latest)
                    self.assertContains(response, "2024-02-01")
                    self.assertIn("2024-02-01", generate_member_csv([paid]))

    def test_filter_choices_show_default_and_allow_all(self):
        response = self.client.get(self.url)
        changelist = response.context["cl"]
        payment_filter = next(
            spec for spec in changelist.filter_specs if spec.title == "Betalt"
        )
        choices = list(payment_filter.choices(changelist))
        self.assertEqual(
            [(choice["display"], choice["selected"]) for choice in choices],
            [("Ja", True), ("Nej", False), ("Alle", False)],
        )
        self.assertIn("payment_status=all", choices[2]["query_string"])

    def test_summary_export_uses_selected_members_and_payment_cutoff(self):
        union = UnionFactory(name="Eksempelforening")
        other_union = UnionFactory(name="Anden forening")
        start = date(2026, 1, 1)
        end = date(2026, 12, 31)
        members = [
            MemberFactory(union=union, member_since=start, member_until=end)
            for _ in range(5)
        ]
        boundary = MemberFactory(
            union=other_union,
            member_since=date(2026, 6, 1),
            member_until=date(2026, 6, 1),
        )
        outside = MemberFactory(
            union=union, member_since=date(2026, 6, 2), member_until=end
        )
        expired = MemberFactory(
            union=union, member_since=start, member_until=date(2026, 5, 31)
        )
        MemberFactory(union=union, member_since=start, member_until=end)

        for member, confirmed_at in (
            (members[0], datetime(2026, 6, 1, 21, 59, tzinfo=timezone.utc)),
            (members[0], datetime(2026, 7, 1, 12, tzinfo=timezone.utc)),
            (members[1], datetime(2026, 6, 1, 22, 0, tzinfo=timezone.utc)),
            (boundary, datetime(2026, 5, 31, 12, tzinfo=timezone.utc)),
        ):
            Payment.objects.create(
                member=member,
                family=member.person.family,
                body_text="Medlemskab",
                confirmed_at=confirmed_at,
            )
        Payment.objects.create(
            member=members[2],
            family=members[2].person.family,
            body_text="Medlemskab",
            accepted_at=self.earlier,
        )

        selected = [member.pk for member in members + [boundary, outside, expired]]
        data = {
            "action": "export_csv_member_summary",
            "_selected_action": selected,
        }
        url = self.url + "?payment_status=all"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type="date"')
        self.assertContains(response, 'min="2026-01-01"')
        response = self.client.post(
            url, {**data, "export_summary": "Eksporter CSV", "date": "2026-06-01"}
        )
        self.assertEqual(response.status_code, 200)
        rows = list(
            csv.reader(StringIO(response.content.decode("utf-8-sig")), delimiter=";")
        )
        self.assertEqual(
            rows,
            [
                [
                    "Forening",
                    "Betalt senest 2026-06-01",
                    "Betalt senere eller ikke betalt",
                ],
                ["Anden forening", "1", "0"],
                ["Eksempelforening", "1", "4"],
            ],
        )

    def test_summary_export_rejects_invalid_date(self):
        response = self.client.post(
            self.url + "?payment_status=all",
            {
                "action": "export_csv_member_summary",
                "_selected_action": [self.paid.pk],
                "export_summary": "Eksporter CSV",
                "date": "ikke-en-dato",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_summary_export_date_lower_boundary(self):
        data = {
            "action": "export_csv_member_summary",
            "_selected_action": [self.paid.pk],
            "export_summary": "1",
        }
        url = self.url + "?payment_status=all"
        response = self.client.post(url, {**data, "date": "2025-12-31"})
        self.assertContains(response, "Datoen skal være 1. januar 2026 eller senere.")
        self.assertTrue(response.context["form"].has_error("date"))

        response = self.client.post(url, {**data, "date": "2026-01-01"})
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")

    def test_summary_minimum_date_updates_help_and_validation(self):
        with (
            patch(
                "members.admin.member_admin.MEMBER_SUMMARY_MIN_DATE", date(2027, 2, 3)
            ),
            translation.override("da"),
        ):
            form = MemberSummaryExportForm({"date": "2027-02-02"})
            self.assertEqual(form.fields["date"].widget.attrs["min"], "2027-02-03")
            self.assertEqual(
                form.fields["date"].help_text,
                "Datoen skal være 3. februar 2027 eller senere.",
            )
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors["date"],
                ["Datoen skal være 3. februar 2027 eller senere."],
            )

    def test_summary_export_requires_permission(self):
        user = User.objects.create_user(username="staff", is_staff=True)
        PersonFactory(user=user)
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="members", codename="view_member"
            )
        )
        AdminUserInformation.objects.create(user=user).unions.add(self.paid.union)
        self.client.force_login(user)
        url = self.url + "?payment_status=all"
        data = {
            "action": "export_csv_member_summary",
            "_selected_action": [self.paid.pk],
            "export_summary": "1",
            "date": "2026-01-01",
        }
        response = self.client.get(url)
        self.assertNotContains(response, "export_csv_member_summary")
        response = self.client.post(url, data)
        self.assertNotEqual(response.get("Content-Type"), "text/csv; charset=utf-8")

        request = RequestFactory().post(url, data)
        request.user = user
        member_admin = MemberAdmin(Member, admin.site)
        with self.assertRaises(PermissionDenied):
            member_admin.export_csv_member_summary(request, Member.objects.all())

        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="members", codename="member_export_summary"
            )
        )
        response = self.client.get(url)
        self.assertContains(response, "export_csv_member_summary")
        response = self.client.post(url, data)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
