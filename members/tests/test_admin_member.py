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

from members.admin.admin_actions import MemberSummaryExportForm
from members.admin.member_admin import MemberAdmin, generate_member_csv
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
            ({}, {self.paid.pk, self.unpaid.pk, self.no_payment.pk}),
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

    def test_payment_date_hidden_for_invalid_latest_payment(self):
        invalid_members = []
        for field in ("cancelled_at", "refunded_at", "rejected_at"):
            member = MemberFactory()
            invalid_members.append(member)
            for confirmed_at, extra in (
                (self.earlier, {}),
                (self.latest, {field: self.latest}),
                (None, {}),
            ):
                Payment.objects.create(
                    member=member,
                    family=member.person.family,
                    body_text="Medlemskab",
                    confirmed_at=confirmed_at,
                    **extra,
                )

        invalid_ids = {member.pk for member in invalid_members}
        for status, expected in (
            (None, invalid_ids | {self.paid.pk, self.unpaid.pk, self.no_payment.pk}),
            ("yes", {self.paid.pk}),
            ("no", invalid_ids | {self.unpaid.pk, self.no_payment.pk}),
            ("all", invalid_ids | {self.paid.pk, self.unpaid.pk, self.no_payment.pk}),
        ):
            with self.subTest(status=status):
                parameters = {"payment_status": status} if status else {}
                response = self.client.get(self.url, parameters)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    {member.pk for member in response.context["cl"].result_list},
                    expected,
                )

        response = self.client.get(self.url, {"payment_status": "all"})
        results = {member.pk: member for member in response.context["cl"].result_list}
        member_admin = MemberAdmin(Member, admin.site)
        for member in invalid_members:
            with self.subTest(member=member.pk):
                self.assertIsNone(results[member.pk].latest_payment_confirmed_at)
                self.assertEqual(member_admin.confirmed_at(results[member.pk]), "")
        self.assertEqual(member_admin.confirmed_at(results[self.paid.pk]), "2024-02-01")

    def test_filter_choices_show_default_and_allow_all(self):
        response = self.client.get(self.url)
        changelist = response.context["cl"]
        payment_filter = next(
            spec for spec in changelist.filter_specs if spec.title == "Betalt"
        )
        choices = list(payment_filter.choices(changelist))
        self.assertEqual(
            [(choice["display"], choice["selected"]) for choice in choices],
            [("Ja", False), ("Nej", False), ("Alle", True)],
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
                "members.admin.admin_actions.MEMBER_SUMMARY_MIN_DATE", date(2027, 2, 3)
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

    def test_union_summary_exports_only_selected_unions(self):
        union = UnionFactory(name="Valgt forening")
        other_union = UnionFactory(name="Anden valgt forening")
        excluded_union = UnionFactory(name="Ikke valgt forening")
        for selected_union in (union, other_union, excluded_union):
            member = MemberFactory(
                union=selected_union,
                member_since=date(2026, 1, 1),
                member_until=date(2026, 12, 31),
            )
            if selected_union == union:
                Payment.objects.create(
                    member=member,
                    family=member.person.family,
                    body_text="Medlemskab",
                    confirmed_at=datetime(2026, 3, 1, 12, tzinfo=timezone.utc),
                )
        url = reverse("admin:members_union_changelist")
        data = {
            "action": "export_csv_member_summary",
            "_selected_action": [union.pk, other_union.pk],
        }
        response = self.client.post(url, data)
        self.assertContains(response, "medlemskaber i de valgte foreninger")
        self.assertContains(response, "Tilbage til foreningsoversigten")
        self.assertEqual(
            {obj.pk for obj in response.context["queryset"]},
            {union.pk, other_union.pk},
        )
        response = self.client.post(
            url, {**data, "export_summary": "1", "date": "2026-06-01"}
        )
        rows = list(
            csv.reader(StringIO(response.content.decode("utf-8-sig")), delimiter=";")
        )
        self.assertEqual(
            rows[1:],
            [["Anden valgt forening", "0", "1"], ["Valgt forening", "1", "0"]],
        )
        response = self.client.post(
            url, {**data, "export_summary": "1", "date": "2025-12-31"}
        )
        self.assertTrue(response.context["form"].has_error("date"))

    def test_union_summary_permission_and_union_access(self):
        user = User.objects.create_user(username="union-staff", is_staff=True)
        PersonFactory(user=user)
        AdminUserInformation.objects.create(user=user).unions.add(self.paid.union)
        hidden = MemberFactory(
            member_since=date(2026, 1, 1), member_until=date(2026, 12, 31)
        )
        self.paid.member_since = date(2026, 1, 1)
        self.paid.member_until = date(2026, 12, 31)
        self.paid.save()
        self.client.force_login(user)
        url = reverse("admin:members_union_changelist")
        data = {
            "action": "export_csv_member_summary",
            "_selected_action": [self.paid.union_id, hidden.union_id],
            "export_summary": "1",
            "date": "2026-06-01",
        }
        self.assertNotContains(self.client.get(url), "export_csv_member_summary")
        self.assertNotEqual(
            self.client.post(url, data).get("Content-Type"), "text/csv; charset=utf-8"
        )
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="members", codename="member_export_summary"
            )
        )
        self.assertContains(self.client.get(url), "export_csv_member_summary")
        response = self.client.post(url, data)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        rows = list(
            csv.reader(StringIO(response.content.decode("utf-8-sig")), delimiter=";")
        )
        self.assertEqual(rows[1:], [[self.paid.union.name, "1", "0"]])
