from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import RequestFactory, TestCase

from members.admin.volunteer_admin import (
    VolunteerAdmin,
    VolunteerAdminForm,
    VolunteerVisibilityListFilter,
    VolunteerActivityListFilter,
    VolunteerUserConfirmationStatusListFilter,
)
from members.models import AdminUserInformation, EmailItem, EmailTemplate, Volunteer
from members.tests.factories import (
    ActivityFactory,
    DepartmentFactory,
    PersonFactory,
    VolunteerFactory,
)


class TestVolunteerAdmin(TestCase):
    class DummyChangeList:
        add_facets = False

        def get_query_string(self, new_params=None, remove=None):
            return ""

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = VolunteerAdmin(Volunteer, admin.site)
        self.user = get_user_model().objects.create_user(
            username="volunteer-admin",
            password="password",
            is_staff=True,
        )
        self.superuser = get_user_model().objects.create_user(
            username="super-volunteer-admin",
            password="password",
            is_staff=True,
            is_superuser=True,
        )

        self.direct_department = DepartmentFactory(name="Odense", closed_dtm=None)
        self.other_department = DepartmentFactory(name="Aarhus", closed_dtm=None)

        self.admin_info = AdminUserInformation.objects.create(user=self.user)
        self.admin_info.departments.add(self.direct_department)

        self.direct_volunteer = VolunteerFactory(
            department=self.direct_department,
            removed=None,
        )
        self.shared_other_volunteer = VolunteerFactory(
            department=self.other_department,
            person=PersonFactory(
                allow_contact_from_cpdk=False,
                allow_contact_from_other=True,
                address_invalid=True,
            ),
            removed=None,
        )
        self.shared_cpdk_volunteer = VolunteerFactory(
            department=self.other_department,
            person=PersonFactory(
                allow_contact_from_cpdk=True,
                allow_contact_from_other=False,
                address_invalid=True,
            ),
            removed=None,
        )
        self.activity = ActivityFactory(
            department=self.direct_department,
            end_date="2026-06-30",
        )
        EmailTemplate.objects.create(idname="ACT_INVITE", subject="test")

    def make_request(self, params=None):
        request = self.factory.get("/admin/members/volunteer/", params or {})
        request.user = self.user
        return request

    def make_post_request(self, params=None):
        request = self.factory.post("/admin/members/volunteer/", params or {})
        request.user = self.user
        setattr(request, "session", self.client.session)
        setattr(request, "_messages", FallbackStorage(request))
        return request

    def test_default_queryset_only_shows_direct_departments(self):
        queryset = self.admin.get_queryset(self.make_request())

        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            {self.direct_volunteer.id},
        )

    def test_actions_include_invite_to_activity(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_volunteer")
        )

        actions = self.admin.get_actions(self.make_request())

        self.assertIn("invite_selected_person_to_activity", actions)
        self.assertEqual(
            actions["invite_selected_person_to_activity"][2],
            "Inviter valgte person til en aktivitet",
        )
        self.assertIn("create_volunteer_action", actions)
        self.assertIn("export_volunteer_info_csv", actions)

    def test_list_display_includes_postcode_after_email(self):
        self.assertEqual(
            self.admin.list_display,
            (
                "get_person_name",
                "get_person_email",
                "get_person_zipcode",
                "department",
                "get_activity_name",
                "get_allow_contact_from_cpdk",
                "get_allow_contact_from_other",
                "start_date",
                "end_date",
            ),
        )

    def test_superuser_list_display_includes_user_confirmation_status(self):
        request = self.make_request()
        request.user = self.superuser

        list_display = self.admin.get_list_display(request)

        self.assertIn("get_user_confirmation_status", list_display)

    def test_non_superuser_list_display_excludes_user_confirmation_status(self):
        list_display = self.admin.get_list_display(self.make_request())

        self.assertNotIn("get_user_confirmation_status", list_display)

    def test_superuser_list_filter_includes_user_confirmation_status_filter(self):
        request = self.make_request()
        request.user = self.superuser

        list_filter = self.admin.get_list_filter(request)

        self.assertIn(VolunteerUserConfirmationStatusListFilter, list_filter)

    def test_non_superuser_list_filter_excludes_user_confirmation_status_filter(self):
        list_filter = self.admin.get_list_filter(self.make_request())

        self.assertNotIn(VolunteerUserConfirmationStatusListFilter, list_filter)

    def test_activity_is_not_an_autocomplete_field(self):
        self.assertEqual(
            self.admin.autocomplete_fields,
            ["person", "department"],
        )

    def test_form_limits_activities_to_selected_department(self):
        other_activity = ActivityFactory(department=self.other_department)

        form = VolunteerAdminForm(data={"department": str(self.direct_department.pk)})

        self.assertIn(self.activity, form.fields["activity"].queryset)
        self.assertNotIn(other_activity, form.fields["activity"].queryset)

    def test_form_sorts_activities_by_start_date_descending(self):
        older_activity = ActivityFactory(
            department=self.direct_department,
            start_date="2026-01-01",
            end_date="2026-02-01",
        )
        newer_activity = ActivityFactory(
            department=self.direct_department,
            start_date="2026-03-01",
            end_date="2026-04-01",
        )

        form = VolunteerAdminForm(data={"department": str(self.direct_department.pk)})

        queryset_ids = list(
            form.fields["activity"].queryset.values_list("id", flat=True)
        )
        self.assertLess(
            queryset_ids.index(newer_activity.id), queryset_ids.index(older_activity.id)
        )

    def test_activity_label_includes_date_range(self):
        activity = ActivityFactory(
            department=self.direct_department,
            name="Frivillig test event",
            start_date="2026-03-01",
            end_date="2026-04-01",
        )

        label = VolunteerAdminForm.activity_label_from_instance(activity)

        self.assertEqual(
            label,
            "[2026-03-01 - 2026-04-01] Frivillig test event",
        )

    def test_filter_lookups_include_direct_departments_and_shared_options(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="see_contacts_shared_with_cpdk"),
            Permission.objects.get(codename="see_contacts_shared_with_other"),
        )

        request = self.make_request()
        visibility_filter = VolunteerVisibilityListFilter(
            request, {}, Volunteer, self.admin
        )
        lookups = dict(visibility_filter.lookups(request, self.admin))

        self.assertEqual(
            lookups[f"department:{self.direct_department.pk}"],
            f"Vis frivillige for {self.direct_department.name}",
        )
        self.assertEqual(lookups["shared_other"], "Delt med andre afdelinger")
        self.assertEqual(lookups["shared_cpdk"], "Delt med Coding Pirates Denmark")

    def test_activity_filter_lookups_only_include_activities_for_visible_volunteers(
        self,
    ):
        visible_activity = ActivityFactory(
            department=self.direct_department,
            name="Visible activity",
        )
        hidden_activity = ActivityFactory(
            department=self.other_department,
            name="Hidden activity",
        )
        self.direct_volunteer.activity = visible_activity
        self.direct_volunteer.save(update_fields=["activity"])
        self.shared_other_volunteer.activity = hidden_activity
        self.shared_other_volunteer.save(update_fields=["activity"])

        request = self.make_request()
        activity_filter = VolunteerActivityListFilter(
            request,
            {},
            Volunteer,
            self.admin,
        )

        lookups = dict(activity_filter.lookups(request, self.admin))

        self.assertIn(str(visible_activity.pk), lookups)
        self.assertNotIn(str(hidden_activity.pk), lookups)

    def test_activity_filter_lookups_handle_visibility_querydict(self):
        visible_activity = ActivityFactory(
            department=self.direct_department,
            name="Visible activity for querydict",
        )
        self.direct_volunteer.activity = visible_activity
        self.direct_volunteer.save(update_fields=["activity"])

        request = self.make_request(
            {"visibility": f"department:{self.direct_department.pk}"}
        )
        activity_filter = VolunteerActivityListFilter(
            request,
            request.GET.copy(),
            Volunteer,
            self.admin,
        )

        lookups = dict(activity_filter.lookups(request, self.admin))

        self.assertIn(str(visible_activity.pk), lookups)

    def test_filter_choices_do_not_include_default_all_option(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="see_contacts_shared_with_cpdk"),
            Permission.objects.get(codename="see_contacts_shared_with_other"),
        )

        request = self.make_request()
        visibility_filter = VolunteerVisibilityListFilter(
            request, {}, Volunteer, self.admin
        )

        choices = list(visibility_filter.choices(self.DummyChangeList()))
        displays = [choice["display"] for choice in choices]

        self.assertNotIn("Alle", displays)
        self.assertIn(f"Vis frivillige for {self.direct_department.name}", displays)
        self.assertIn("Delt med andre afdelinger", displays)
        self.assertIn("Delt med Coding Pirates Denmark", displays)

    def test_default_visibility_filter_uses_first_direct_department(self):
        first_department = DepartmentFactory(name="Aalborg", closed_dtm=None)
        self.admin_info.departments.add(first_department)

        first_department_volunteer = VolunteerFactory(
            department=first_department,
            removed=None,
        )

        request = self.make_request()
        visibility_filter = VolunteerVisibilityListFilter(
            request, {}, Volunteer, self.admin
        )

        filtered_queryset = visibility_filter.queryset(
            request,
            Volunteer.objects.filter(
                pk__in=[
                    first_department_volunteer.pk,
                    self.direct_volunteer.pk,
                    self.shared_other_volunteer.pk,
                ]
            ),
        )

        self.assertEqual(
            set(filtered_queryset.values_list("id", flat=True)),
            {first_department_volunteer.id},
        )

    def test_shared_other_filter_uses_person_contact_flag(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="see_contacts_shared_with_other")
        )
        request = self.make_request({"visibility": "shared_other"})
        queryset = self.admin.get_queryset(request)
        visibility_filter = VolunteerVisibilityListFilter(
            request, {"visibility": "shared_other"}, Volunteer, self.admin
        )

        filtered_queryset = visibility_filter.queryset(request, queryset)

        self.assertEqual(
            set(filtered_queryset.values_list("id", flat=True)),
            {self.shared_other_volunteer.id},
        )

    def test_shared_cpdk_filter_uses_person_contact_flag(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="see_contacts_shared_with_cpdk")
        )
        request = self.make_request({"visibility": "shared_cpdk"})
        queryset = self.admin.get_queryset(request)
        visibility_filter = VolunteerVisibilityListFilter(
            request, {"visibility": "shared_cpdk"}, Volunteer, self.admin
        )

        filtered_queryset = visibility_filter.queryset(request, queryset)

        self.assertEqual(
            set(filtered_queryset.values_list("id", flat=True)),
            {self.shared_cpdk_volunteer.id},
        )

    def test_get_object_allows_opening_shared_volunteer_without_visibility_query(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="see_contacts_shared_with_other"),
            Permission.objects.get(codename="view_volunteer"),
        )

        obj = self.admin.get_object(
            self.make_request(),
            str(self.shared_other_volunteer.pk),
        )

        self.assertEqual(obj, self.shared_other_volunteer)

    def test_shared_volunteer_is_not_changeable_without_department_access(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="see_contacts_shared_with_other"),
            Permission.objects.get(codename="view_volunteer"),
            Permission.objects.get(codename="change_volunteer"),
        )

        self.assertFalse(
            self.admin.has_change_permission(
                self.make_request(),
                self.shared_other_volunteer,
            )
        )

    def test_direct_department_volunteer_is_changeable_with_permission(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_volunteer"),
            Permission.objects.get(codename="change_volunteer"),
        )

        self.assertTrue(
            self.admin.has_change_permission(
                self.make_request(),
                self.direct_volunteer,
            )
        )

    def test_shared_volunteer_fieldsets_only_show_allowed_fields(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="see_contacts_shared_with_other"),
            Permission.objects.get(codename="view_volunteer"),
        )

        fieldsets = self.admin.get_fieldsets(
            self.make_request(),
            obj=self.shared_other_volunteer,
        )

        self.assertEqual(
            fieldsets,
            [
                (
                    "Person data",
                    {
                        "fields": (
                            "get_person_display",
                            "get_person_name",
                            "get_person_email",
                            "get_department_display",
                        )
                    },
                ),
            ],
        )

    def test_direct_department_fieldsets_still_show_full_details(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_volunteer"),
            Permission.objects.get(codename="change_volunteer"),
        )

        fieldsets = self.admin.get_fieldsets(
            self.make_request(),
            obj=self.direct_volunteer,
        )

        self.assertEqual(len(fieldsets), 4)
        self.assertEqual(fieldsets[0][0], "Person data")
        self.assertEqual(
            fieldsets[0][1]["fields"],
            ("get_person_display", "get_person_name", "get_person_email"),
        )
        self.assertEqual(fieldsets[1][0], "Hvad og hvornår")
        self.assertEqual(
            fieldsets[1][1]["fields"],
            ("department", "activity", "start_date", "end_date"),
        )

    def test_direct_department_volunteer_has_readonly_person_and_department(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_volunteer"),
            Permission.objects.get(codename="change_volunteer"),
        )

        readonly_fields = self.admin.get_readonly_fields(
            self.make_request(),
            obj=self.direct_volunteer,
        )

        self.assertIn("get_person_display", readonly_fields)
        self.assertIn("department", readonly_fields)

    def test_add_form_keeps_person_and_department_editable(self):
        readonly_fields = self.admin.get_readonly_fields(self.make_request(), obj=None)

        self.assertNotIn("department", readonly_fields)

    def test_shared_volunteer_is_not_deletable_without_department_access(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="see_contacts_shared_with_other"),
            Permission.objects.get(codename="view_volunteer"),
            Permission.objects.get(codename="delete_volunteer"),
        )

        self.assertFalse(
            self.admin.has_delete_permission(
                self.make_request(),
                self.shared_other_volunteer,
            )
        )

    def test_readonly_form_for_shared_volunteer_does_not_crash_without_activity_field(
        self,
    ):
        self.user.user_permissions.add(
            Permission.objects.get(codename="see_contacts_shared_with_other"),
            Permission.objects.get(codename="view_volunteer"),
        )
        request = self.make_request()

        form_class = self.admin.get_form(
            request,
            obj=self.shared_other_volunteer,
            change=True,
        )
        form = form_class(instance=self.shared_other_volunteer)

        self.assertIsNotNone(form)

    def test_invite_action_intermediate_form_preserves_volunteer_action_name(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_volunteer")
        )
        request = self.make_post_request(
            {
                "action": "invite_selected_person_to_activity",
                "_selected_action": [self.direct_volunteer.pk],
            }
        )

        response = self.admin.invite_selected_person_to_activity(
            request,
            Volunteer.objects.filter(pk=self.direct_volunteer.pk),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'name="action" value="invite_selected_person_to_activity"',
            html=False,
        )

    def test_create_volunteer_action_requires_single_volunteer(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_volunteer")
        )
        request = self.make_post_request()

        response = self.admin.create_volunteer_action(
            request,
            Volunteer.objects.filter(
                pk__in=[self.direct_volunteer.pk, self.shared_other_volunteer.pk]
            ),
        )

        self.assertEqual(response.status_code, 302)

    def test_create_volunteer_action_opens_without_department_or_activity_selected(
        self,
    ):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_volunteer")
        )
        request = self.make_post_request(
            {
                "action": "create_volunteer_action",
                "_selected_action": [self.direct_volunteer.pk],
            },
        )

        response = self.admin.create_volunteer_action(
            request,
            Volunteer.objects.filter(pk=self.direct_volunteer.pk),
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            f'value="{self.direct_department.pk}" selected',
            html=False,
        )
        self.assertContains(response, "--- Ingen aktivitet ---")

    def test_create_volunteer_action_creates_new_volunteer_from_existing_volunteer(
        self,
    ):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_volunteer")
        )
        new_activity = ActivityFactory(department=self.direct_department)
        request = self.make_post_request(
            {
                "action": "create_volunteer_action",
                "department": self.direct_department.pk,
                "activity": new_activity.pk,
                "start_date": "2026-06-07",
                "end_date": "2026-06-30",
                "_selected_action": [self.direct_volunteer.pk],
            },
        )

        response = self.admin.create_volunteer_action(
            request,
            Volunteer.objects.filter(pk=self.direct_volunteer.pk),
        )

        self.assertEqual(response.status_code, 302)

        created_volunteer = Volunteer.objects.exclude(pk=self.direct_volunteer.pk).get(
            person=self.direct_volunteer.person,
            department=self.direct_department,
            activity=new_activity,
        )
        self.assertEqual(str(created_volunteer.start_date), "2026-06-07")
        self.assertEqual(str(created_volunteer.end_date), "2026-06-30")
        self.assertEqual(
            created_volunteer.user_confirmation_status,
            Volunteer.UserConfirmationStatus.WAITING_FOR_USER,
        )
        self.assertTrue(
            EmailItem.objects.filter(
                receiver=self.direct_volunteer.person.email,
                person=self.direct_volunteer.person,
            ).exists()
        )

    def test_create_volunteer_action_refreshes_activities_for_selected_department(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_volunteer")
        )
        self.admin_info.departments.add(self.other_department)
        visible_activity = ActivityFactory(
            department=self.direct_department,
            name="Visible volunteer activity",
        )
        hidden_activity = ActivityFactory(
            department=self.other_department,
            name="Hidden volunteer activity",
        )

        request = self.make_post_request(
            {
                "action": "create_volunteer_action",
                "department": self.direct_department.pk,
                "activity": "",
                "start_date": "2026-06-07",
                "end_date": "",
                "refresh_activity_choices": "1",
                "_selected_action": [self.direct_volunteer.pk],
            },
        )

        response = self.admin.create_volunteer_action(
            request,
            Volunteer.objects.filter(pk=self.direct_volunteer.pk),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"[{visible_activity.start_date:%Y-%m-%d} - {visible_activity.end_date:%Y-%m-%d}] {visible_activity.name}",
        )
        self.assertNotContains(response, hidden_activity.name)
        self.assertContains(response, "⏳ Henter aktiviteter fra databasen ...")
