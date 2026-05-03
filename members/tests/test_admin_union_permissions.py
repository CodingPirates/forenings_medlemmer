from django.contrib.admin import AdminSite
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from members.admin.union_admin import UnionAdmin
from members.models import Address, AdminUserInformation, Department, Union


class UnionAdminPermissionsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.model_admin = UnionAdmin(Union, self.site)

        self.department_admin = User.objects.create_user(
            username="department-admin",
            password="password",
            email="department-admin@example.com",
            is_staff=True,
        )
        self.admin_info = AdminUserInformation.objects.create(
            user=self.department_admin
        )

        self.union_admin = User.objects.create_user(
            username="union-admin",
            password="password",
            email="union-admin@example.com",
            is_staff=True,
        )
        self.union_admin_info = AdminUserInformation.objects.create(
            user=self.union_admin
        )

        self.address = Address.objects.create(
            streetname="Adminvej",
            city="København",
            zipcode="2400",
            region="Region Hovedstaden",
        )
        self.visible_union = Union.objects.create(name="Vanløse", address=self.address)
        self.hidden_union = Union.objects.create(name="Aarhus", address=self.address)

        self.department = Department.objects.create(
            name="Vanløse afdeling",
            address=self.address,
            union=self.visible_union,
        )
        self.admin_info.departments.add(self.department)
        self.union_admin_info.unions.add(self.visible_union)

    def test_get_unions_admin_includes_unions_from_admin_departments(self):
        unions = AdminUserInformation.get_unions_admin(self.department_admin)

        self.assertQuerySetEqual(
            unions.order_by("pk"),
            [self.visible_union],
            transform=lambda union: union,
        )

    def test_union_admin_queryset_includes_department_union(self):
        request = self.factory.get("/admin/members/union/")
        request.user = self.department_admin

        queryset = self.model_admin.get_queryset(request)

        self.assertQuerySetEqual(
            queryset.order_by("pk"),
            [self.visible_union],
            transform=lambda union: union,
        )

    def test_union_admin_has_view_permission_for_department_union(self):
        request = self.factory.get("/admin/members/union/autocomplete/")
        request.user = self.department_admin

        self.assertTrue(self.model_admin.has_view_permission(request))
        self.assertTrue(
            self.model_admin.has_view_permission(request, obj=self.visible_union)
        )
        self.assertFalse(
            self.model_admin.has_view_permission(request, obj=self.hidden_union)
        )

    def test_department_only_user_hides_sensitive_info_fields(self):
        permission_codenames = [
            "show_ledger_account",
            "show_new_membership_model",
        ]
        self.department_admin.user_permissions.add(
            *Permission.objects.filter(codename__in=permission_codenames)
        )

        request = self.factory.get(
            f"/admin/members/union/{self.visible_union.pk}/change/"
        )
        request.user = self.department_admin

        fieldsets = self.model_admin.get_fieldsets(request, obj=self.visible_union)
        info_fieldset = next(opts for title, opts in fieldsets if title == "Info")

        self.assertEqual(
            tuple(info_fieldset["fields"]),
            (
                "statues",
                "founded_at",
                "closed_at",
                "membership_price_in_dkk",
            ),
        )

    def test_direct_union_access_keeps_sensitive_info_fields(self):
        permission_codenames = [
            "change_union",
            "show_ledger_account",
            "show_new_membership_model",
        ]
        self.union_admin.user_permissions.add(
            *Permission.objects.filter(codename__in=permission_codenames)
        )

        request = self.factory.get(
            f"/admin/members/union/{self.visible_union.pk}/change/"
        )
        request.user = self.union_admin

        fieldsets = self.model_admin.get_fieldsets(request, obj=self.visible_union)
        info_fieldset = next(opts for title, opts in fieldsets if title == "Info")

        self.assertEqual(
            tuple(info_fieldset["fields"]),
            (
                "bank_main_org",
                "bank_account",
                "statues",
                "founded_at",
                "closed_at",
                "memberships_allowed_at",
                "membership_price_in_dkk",
                "gl_account",
                "new_membership_model_activated_at",
            ),
        )

    def test_readonly_user_gets_readonly_union_help_text(self):
        request = self.factory.get(
            f"/admin/members/union/{self.visible_union.pk}/change/"
        )
        request.user = self.department_admin

        fieldsets = self.model_admin.get_fieldsets(request, obj=self.visible_union)
        name_fieldset = next(
            opts for title, opts in fieldsets if title == "Navn og Adresse"
        )

        self.assertEqual(
            name_fieldset["description"],
            "<p>Du har ikke adgang til at ændre denne siden. "
            "Du skal sidde i bestyrelsen for foreningen og derefter "
            "kontakte kontakt@codingpirates.dk<p>",
        )

    def test_change_user_keeps_original_union_help_text(self):
        self.union_admin.user_permissions.add(
            Permission.objects.get(codename="change_union")
        )

        request = self.factory.get(
            f"/admin/members/union/{self.visible_union.pk}/change/"
        )
        request.user = self.union_admin

        fieldsets = self.model_admin.get_fieldsets(request, obj=self.visible_union)
        name_fieldset = next(
            opts for title, opts in fieldsets if title == "Navn og Adresse"
        )

        self.assertEqual(
            name_fieldset["description"],
            "<p>Udfyld navnet på foreningen (f.eks København, \
                        vestjylland) og adressen<p>",
        )
