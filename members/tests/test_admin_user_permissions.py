from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, Permission, User
from django.test import RequestFactory, TestCase

from members.admin.user_admin import UserAdmin


class UserAdminSuperuserStatusPermissionTest(TestCase):
    def setUp(self):
        self.admin = UserAdmin(User, AdminSite())
        self.request = RequestFactory().get("/admin/auth/user/")
        self.user = User.objects.create_user(username="staff", is_staff=True)
        self.request.user = self.user
        self.permission = Permission.objects.get(
            content_type__app_label="members",
            content_type__model="userwithsuperuserview",
            codename="view_superuser_status",
        )

    def assert_superuser_status_visible(self, visible):
        self.assertEqual(
            "is_superuser" in self.admin.get_list_display(self.request), visible
        )
        self.assertEqual(
            "is_superuser" in self.admin.get_list_filter(self.request), visible
        )

    def test_staff_without_permission_cannot_see_status(self):
        self.assert_superuser_status_visible(False)

    def test_staff_with_direct_permission_can_see_status(self):
        self.user.user_permissions.add(self.permission)
        self.assert_superuser_status_visible(True)

    def test_staff_with_group_permission_can_see_status(self):
        group = Group.objects.create(name="status viewers")
        group.permissions.add(self.permission)
        self.user.groups.add(group)
        self.assert_superuser_status_visible(True)

    def test_superuser_can_see_status_without_explicit_permission(self):
        self.user.is_superuser = True
        self.assert_superuser_status_visible(True)
