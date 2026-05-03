from django.contrib.admin import AdminSite
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
