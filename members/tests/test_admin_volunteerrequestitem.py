from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from members.admin.volunteerrequestitem_admin import (
    VolunteerRequestItemAdmin,
    VolunteerRequestItemListFilter,
)
from members.models import AdminUserInformation, VolunteerRequest, VolunteerRequestItem
from members.tests.factories import DepartmentFactory, PersonFactory


class TestVolunteerRequestItemAdmin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = VolunteerRequestItemAdmin(VolunteerRequestItem, admin.site)
        self.user = get_user_model().objects.create_user(
            username="volunteerrequest-admin",
            password="password",
            is_staff=True,
        )
        self.superuser = get_user_model().objects.create_user(
            username="volunteerrequest-superuser",
            password="password",
            is_staff=True,
            is_superuser=True,
        )

        self.direct_department = DepartmentFactory(name="Odense", closed_dtm=None)
        self.other_department = DepartmentFactory(name="Aarhus", closed_dtm=None)
        self.admin_info = AdminUserInformation.objects.create(user=self.user)
        self.admin_info.departments.add(self.direct_department)

        self.volunteer_request = VolunteerRequest.objects.create(
            person=PersonFactory(address_invalid=True),
            info_reference="LinkedIn",
            info_whishes="Jeg vil gerne hjælpe.",
        )
        self.direct_item = VolunteerRequestItem.objects.create(
            volunteer_request=self.volunteer_request,
            department=self.direct_department,
        )
        self.other_item = VolunteerRequestItem.objects.create(
            volunteer_request=self.volunteer_request,
            department=self.other_department,
        )

    def make_request(self, user=None, params=None):
        request = self.factory.get(
            "/admin/members/volunteerrequestitem/",
            params or {},
        )
        request.user = user or self.user
        return request

    def test_queryset_only_shows_accessible_departments_for_regular_admin(self):
        queryset = self.admin.get_queryset(self.make_request())

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            {self.direct_item.id},
        )

    def test_queryset_shows_all_departments_for_superuser(self):
        queryset = self.admin.get_queryset(self.make_request(user=self.superuser))

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            {self.direct_item.id, self.other_item.id},
        )

    def test_department_filter_applies_selected_department(self):
        request = self.make_request(
            params={"department": str(self.direct_department.pk)}
        )
        department_filter = VolunteerRequestItemListFilter(
            request,
            {"department": str(self.direct_department.pk)},
            VolunteerRequestItem,
            self.admin,
        )

        filtered_queryset = department_filter.queryset(
            request,
            VolunteerRequestItem.objects.filter(
                pk__in=[self.direct_item.pk, self.other_item.pk]
            ),
        )

        self.assertEqual(
            set(filtered_queryset.values_list("id", flat=True)),
            {self.direct_item.id},
        )
