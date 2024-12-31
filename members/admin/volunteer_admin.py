import codecs
from django.contrib import admin
from django.http import HttpResponse
from django import forms
from django.db.models import Q

from members.models import (
    Volunteer,
    Department,
    AdminUserInformation,
    Activity,
)


class VolunteerDepartmentListFilter(admin.SimpleListFilter):
    title = "Afdelinger"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        departments = []
        for d in (
            Department.objects.filter(
                volunteer__department__in=AdminUserInformation.get_departments_admin(
                    request.user
                )
            )
            .order_by("name")
            .distinct()
        ):
            departments.append((str(d.pk), str(d)))
        return departments

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(department__pk=self.value())


class VolunteerActivityListFilter(admin.SimpleListFilter):
    title = "Aktiviteter"
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activities = []
        for a in (
            Activity.objects.filter(
                volunteer__activity__department__in=AdminUserInformation.get_departments_admin(
                    request.user
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "department" in self.data:
            print(f"*1")
            try:
                department_id = int(self.data.get("department"))
                self.fields["activity"].queryset = Activity.objects.filter(
                    department_id=department_id,
                    activitytype__id__in=["FORLØB", "ARRANGEMENT"],
                ).order_by("name")
                # self.fields["activity"].label_from_instance = self.label_from_instance
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Activity queryset
        elif self.instance.pk:
            print(f"*2")
            self.fields["activity"].queryset = (
                self.instance.department.activity_set.filter(
                    activitytype__id__in=["FORLØB", "ARRANGEMENT"]
                ).order_by("name")
            )
            print(f' activity: {self.fields["activity"].queryset}')
            print(f" initial: {self.instance.activity}")
            # self.fields["activity"].label_from_instance = self.label_from_instance
            self.fields["activity"].initial = self.instance.activity
        else:
            print(f"*3")
            self.fields["activity"].queryset = (
                Activity.objects.none()
            )  # Set to empty queryset initially

    # def label_from_instance(self, obj):
    #    return f"[{obj.start_date} - {obj.end_date}] {obj.name}"


class VolunteerAdmin(admin.ModelAdmin):
    form = VolunteerAdminForm

    list_display = (
        "get_person_name",
        "get_person_email",
        "department",
        "activity",
        "start_date",
        "end_date",
    )
    list_filter = (
        VolunteerDepartmentListFilter,
        VolunteerActivityListFilter,
    )

    readonly_fields = (
        "get_person_name",
        "get_person_email",
        "added_at",
        "confirmed",
        "removed",
    )

    autocomplete_fields = [
        "person", "department", "activity", ]

    actions = [
        "export_volunteer_info_csv",
    ]

    class Media:
        js = ("members/js/volunteer_admin.js",)

    def get_fieldsets(self, request, obj=None):
        # if not obj:
        #     return self.add_fieldsets

        # Check for super user (or special perm)

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
                        "person",
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
            ("Ekstra info", {"fields": (info_fields,)}),
        ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
            return qs
        else:
            departments = AdminUserInformation.get_departments_admin(request.user)
            return qs.filter(department__in=departments)
    
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        queryset = queryset.filter(activity__activitytype_id__in=["FORLØB", "ARRANGEMENT"])
        return queryset, use_distinct
    

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        '''
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
        '''
        if db_field.name == "activity":
            if "department" in request.GET:
                department_id = request.GET.get("department")
                kwargs["queryset"] = Activity.objects.filter(
                    department_id=department_id,
                    activity__activitytype_id__in=["FORLØB", "ARRANGEMENT"]
                ).order_by("name")
            else:
                kwargs["queryset"] = Activity.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_person_name(self, obj):
        return obj.person.name

    get_person_name.short_description = "Navn"
    get_person_name.admin_order_field = "person__name"

    def get_person_email(self, obj):
        return obj.person.email

    get_person_email.short_description = "Email"
    get_person_email.admin_order_field = "person__email"

    def get_activity_name(self, obj):
        return obj.activity.name
    
    get_activity_name.short_description = "Aktivitet"
    get_activity_name.admin_order_field = "activity__name"

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
