import codecs
from django.contrib import admin
from django.http import HttpResponse
from django import forms
from django.db.models import Q
from forenings_medlemmer import settings
from members.models import Volunteer, Department, Activity, AdminUserInformation
from members.admin.admin_actions import AdminActions


class VolunteerVisibilityListFilter(admin.SimpleListFilter):
    title = "Visning"
    parameter_name = "visibility"

    def get_default_department(self, request):
        return (
            Department.objects.filter(adminuserinformation__user=request.user)
            .order_by("name")
            .distinct()
            .first()
        )

    def choices(self, changelist):
        for index, choice in enumerate(super().choices(changelist)):
            if index == 0:
                continue
            yield choice

    def lookups(self, request, model_admin):
        lookups = []

        if request.user.is_superuser:
            lookups.append(("all", "Alle Frivillige"))

        for department in (
            Department.objects.filter(adminuserinformation__user=request.user)
            .order_by("name")
            .distinct()
        ):
            lookups.append(
                (
                    f"department:{department.pk}",
                    f"Vis frivillige for {department.name}",
                )
            )

        if request.user.has_perm("members.see_contacts_shared_with_other"):
            lookups.append(("shared_other", "Delt med andre afdelinger"))

        if request.user.has_perm("members.see_contacts_shared_with_cpdk"):
            lookups.append(("shared_cpdk", "Delt med Coding Pirates Denmark"))

        return lookups

    def queryset(self, request, queryset):
        if self.value() is None:
            if request.user.is_superuser or request.user.has_perm(
                "members.view_all_departments"
            ):
                return queryset

            default_department = self.get_default_department(request)
            if default_department is not None:
                return queryset.filter(department=default_department)
            return queryset

        if self.value().startswith("department:"):
            return queryset.filter(department__pk=self.value().split(":", 1)[1])

        if self.value() == "shared_other":
            return queryset.filter(person__allow_contact_from_other=True)

        if self.value() == "shared_cpdk":
            return queryset.filter(person__allow_contact_from_cpdk=True)

        if self.value() == "all":
            return queryset

        return queryset


class VolunteerActivityListFilter(admin.SimpleListFilter):
    title = "Aktiviteter"
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        visible_queryset = model_admin.get_queryset(request)
        visibility_filter = VolunteerVisibilityListFilter(
            request,
            request.GET.copy(),
            Volunteer,
            model_admin,
        )
        visible_queryset = visibility_filter.queryset(request, visible_queryset)

        activities = []
        for a in (
            Activity.objects.filter(
                pk__in=visible_queryset.exclude(activity__isnull=True).values_list(
                    "activity_id", flat=True
                )
            )
            .order_by("name")
            .distinct()
        ):
            activities.append((str(a.id), str(a)))
        return activities

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__pk=self.value())


class VolunteerAdminForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = "__all__"

    @staticmethod
    def activity_label_from_instance(obj):
        def format_date(value):
            if not value:
                return "-"
            if hasattr(value, "strftime"):
                return value.strftime("%Y-%m-%d")
            return str(value)

        start_date = format_date(obj.start_date)
        end_date = format_date(obj.end_date)
        return f"[{start_date} - {end_date}] {obj.name}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "activity" not in self.fields:
            return

        self.fields["activity"].label_from_instance = self.activity_label_from_instance
        if "department" in self.data:
            try:
                department_id = int(self.data.get("department"))
                self.fields["activity"].queryset = Activity.objects.filter(
                    department_id=department_id,
                    activitytype__id__in=["FORLØB", "ARRANGEMENT"],
                ).order_by("-start_date", "name")
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Activity queryset
        elif self.instance.pk:
            self.fields["activity"].queryset = (
                self.instance.department.activity_set.filter(
                    activitytype__id__in=["FORLØB", "ARRANGEMENT"]
                ).order_by("-start_date", "name")
            )
            self.fields["activity"].initial = self.instance.activity
        else:
            self.fields["activity"].queryset = Activity.objects.none()


class VolunteerUserConfirmationStatusListFilter(admin.SimpleListFilter):
    title = "Brugerbekræftelse"
    parameter_name = "user_confirmation_status"

    def lookups(self, request, model_admin):
        return Volunteer.UserConfirmationStatus.choices

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(user_confirmation_status=self.value())


class VolunteerAdmin(admin.ModelAdmin):
    form = VolunteerAdminForm

    @staticmethod
    def user_manages_department(user, department):
        if user.is_superuser or user.has_perm("members.view_all_departments"):
            return True

        if department is None:
            return False

        return (
            AdminUserInformation.get_departments_admin(user)
            .filter(pk=department.pk)
            .exists()
        )

    list_per_page = settings.LIST_PER_PAGE
    search_fields = [
        "person__name",
        "person__email",
        "department__name",
        "activity__name",
    ]

    date_hierarchy = "start_date"

    list_display = (
        "get_person_name",
        "get_person_email",
        "get_person_zipcode",
        "department",
        "get_activity_name",
        "get_allow_contact_from_cpdk",
        "get_allow_contact_from_other",
        "start_date",
        "end_date",
    )
    list_filter = (
        VolunteerVisibilityListFilter,
        VolunteerActivityListFilter,
        "start_date",
        "end_date",
    )

    readonly_fields = (
        "get_person_display",
        "get_department_display",
        "get_person_name",
        "get_person_email",
        "get_allow_contact_from_cpdk",
        "get_allow_contact_from_other",
        "added_at",
        "confirmed",
        "removed",
    )

    autocomplete_fields = [
        "person",
        "department",
    ]

    actions = [
        AdminActions.create_volunteer_action,
        "invite_selected_person_to_activity",
        "export_volunteer_info_csv",
    ]

    class Media:
        js = ("members/js/volunteer_admin.js",)

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))

        if request.user.is_superuser:
            list_display.append("get_user_confirmation_status")

        return tuple(list_display)

    def get_list_filter(self, request):
        list_filter = list(super().get_list_filter(request))

        if request.user.is_superuser:
            list_filter.append(VolunteerUserConfirmationStatusListFilter)

        return tuple(list_filter)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj and self.user_manages_department(request.user, obj.department):
            readonly_fields.append("department")

        return tuple(readonly_fields)

    def get_fieldsets(self, request, obj=None):
        if obj and not self.user_manages_department(request.user, obj.department):
            return [
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
            ]

        info_fields = ("confirmed",)

        if request.user.is_superuser:
            info_fields = (
                "added_at",
                "confirmed",
                "removed",
            )

        return [
            (
                "Person data",
                {
                    "fields": (
                        "get_person_display" if obj else "person",
                        "get_person_name",
                        "get_person_email",
                    )
                },
            ),
            (
                "Hvad og hvornår",
                {
                    "fields": (
                        "department",
                        "activity",
                        "start_date",
                        "end_date",
                    )
                },
            ),
            (
                "Kontaktdeling",
                {
                    "fields": (
                        "get_allow_contact_from_cpdk",
                        "get_allow_contact_from_other",
                    )
                },
            ),
            ("Ekstra info", {"fields": (info_fields,)}),
        ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            visibility = request.GET.get("visibility")
            departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )

            base_filter = Q(department__in=departments)

            if request.user.has_perm("members.see_contacts_shared_with_other"):
                base_filter |= Q(person__allow_contact_from_other=True)

            if request.user.has_perm("members.see_contacts_shared_with_cpdk"):
                base_filter |= Q(person__allow_contact_from_cpdk=True)

            qs = qs.filter(base_filter).distinct()

            if visibility == "shared_other" and request.user.has_perm(
                "members.see_contacts_shared_with_other"
            ):
                return qs.filter(person__allow_contact_from_other=True)

            if visibility == "shared_cpdk" and request.user.has_perm(
                "members.see_contacts_shared_with_cpdk"
            ):
                return qs.filter(person__allow_contact_from_cpdk=True)

            return qs

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        queryset = queryset.filter(
            Q(activity__activitytype_id__in=["FORLØB", "ARRANGEMENT"])
            | Q(activity__isnull=True)
        )
        return queryset, use_distinct

    def has_change_permission(self, request, obj=None):
        has_change = super().has_change_permission(request, obj)
        if obj is None or not has_change:
            return has_change

        return self.user_manages_department(request.user, obj.department)

    def has_delete_permission(self, request, obj=None):
        has_delete = super().has_delete_permission(request, obj)
        if obj is None or not has_delete:
            return has_delete

        return self.user_manages_department(request.user, obj.department)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        # Only show departments that user can access
        if db_field.name == "department":
            if request.user.is_superuser or request.user.has_perm(
                "members.view_all_departments"
            ):
                kwargs["queryset"] = Department.objects.all()
            else:
                kwargs["queryset"] = Department.objects.filter(
                    adminuserinformation__user=request.user
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        """
        if db_field.name == "activity":
            if "department" in request.GET:
                department_id = request.GET.get("department")
                kwargs["queryset"] = Activity.objects.filter(
                    department_id=department_id,
                    activity__activitytype_id__in=["FORLØB", "ARRANGEMENT"],
                ).order_by("-start_date", "name")
            else:
                kwargs["queryset"] = Activity.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_person_name(self, obj):
        return obj.person.name

    def get_person_display(self, obj):
        return str(obj.person)

    get_person_display.short_description = "Person"
    get_person_name.short_description = "Navn"
    get_person_name.admin_order_field = "person__name"

    def get_person_email(self, obj):
        return obj.person.email

    get_person_email.short_description = "Email"
    get_person_email.admin_order_field = "person__email"

    def get_department_display(self, obj):
        return str(obj.department)

    get_department_display.short_description = "Afdeling"

    def get_person_zipcode(self, obj):
        return obj.person.zipcode

    get_person_zipcode.short_description = "Post nr"
    get_person_zipcode.admin_order_field = "person__zipcode"

    def get_activity_name(self, obj):
        if obj.activity is not None:
            return obj.activity.name
        return ""

    get_activity_name.short_description = "Aktivitet"
    get_activity_name.admin_order_field = "activity__name"

    def get_user_confirmation_status(self, obj):
        return obj.get_user_confirmation_status_display()

    get_user_confirmation_status.short_description = "Brugerbekræftelse"
    get_user_confirmation_status.admin_order_field = "user_confirmation_status"

    def get_allow_contact_from_cpdk(self, obj):
        return obj.person.allow_contact_from_cpdk

    get_allow_contact_from_cpdk.short_description = "Delt med CPDK"
    get_allow_contact_from_cpdk.boolean = True
    get_allow_contact_from_cpdk.admin_order_field = "person__allow_contact_from_cpdk"

    def get_allow_contact_from_other(self, obj):
        return obj.person.allow_contact_from_other

    get_allow_contact_from_other.short_description = "Delt med andre"
    get_allow_contact_from_other.boolean = True
    get_allow_contact_from_other.admin_order_field = "person__allow_contact_from_other"

    def export_volunteer_info_csv(self, request, queryset):
        result = """"Forening";"Afdeling";"Aktivitet";"Navn";"Email";"Startdato";"Slutdato"\n"""
        for v in queryset.order_by("start_date"):
            if v.department is not None:
                result += v.department.union.name + ";"
                result += v.department.name + ";"
            else:
                result += ";"
            if v.activity is not None:
                result += v.activity.name
            result += ";"
            result += v.person.name + ";"
            result += v.person.email + ";"
            if v.start_date is not None:
                result += v.start_date.strftime("%Y-%m-%d")
            result += ";"
            if v.end_date is not None:
                result += v.end_date.strftime("%Y-%m-%d")
            result += "\n"

        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("utf-8")}{result}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="FrivilligInfo.csv"'
        return response

    export_volunteer_info_csv.short_description = "Exporter frivilliginfo (CSV)"
    export_volunteer_info_csv.allowed_permissions = ("view",)

    def invite_selected_person_to_activity(self, request, queryset):
        return AdminActions.invite_many_to_activity_action(self, request, queryset)

    invite_selected_person_to_activity.short_description = (
        "Inviter valgte person til en aktivitet"
    )
    invite_selected_person_to_activity.allowed_permissions = ("view",)
