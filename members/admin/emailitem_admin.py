from typing import Any

from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# from members.models import EmailItem
from members.models import (
    Activity,
    AdminUserInformation,
    EmailItem,
)


def get_emailitem_queryset_for_user(request: Any):
    queryset = EmailItem.objects.all()
    if request.user.is_superuser:
        return queryset

    queryset = queryset.exclude(template__idname="SECURITY_TOKEN")

    if request.user.has_perm("members.view_all_departments"):
        return queryset

    departments = AdminUserInformation.get_departments_admin(request.user)
    return queryset.filter(
        Q(department__in=departments) | Q(activity__department__in=departments)
    ).distinct()


def get_filtered_emailitem_queryset(request: Any, excluded_parameters=None):
    if excluded_parameters is None:
        excluded_parameters = set()

    queryset = get_emailitem_queryset_for_user(request)
    filtervalue = None
    queryset, filtervalue = getRequestDateFilter(
        request, "created_dtm__year", queryset, filtervalue
    )
    queryset, filtervalue = getRequestDateFilter(
        request, "created_dtm__month", queryset, filtervalue
    )
    queryset, filtervalue = getRequestDateFilter(
        request, "created_dtm__day", queryset, filtervalue
    )

    union_value = request.GET.get(EmailItemUnionFilter.parameter_name)
    if union_value and EmailItemUnionFilter.parameter_name not in excluded_parameters:
        queryset = queryset.filter(
            Q(department__union_id=union_value)
            | Q(activity__department__union_id=union_value)
        )

    department_value = request.GET.get(EmailItemDepartmentFilter.parameter_name)
    if (
        department_value
        and EmailItemDepartmentFilter.parameter_name not in excluded_parameters
    ):
        queryset = queryset.filter(
            Q(department_id=department_value)
            | Q(activity__department_id=department_value)
        )

    activity_value = request.GET.get(activityFilter.parameter_name)
    if activityFilter.parameter_name not in excluded_parameters:
        if activity_value == "none":
            queryset = queryset.filter(activity__isnull=True)
        elif activity_value:
            queryset = queryset.filter(activity_id=activity_value)

    return queryset, filtervalue


class EmailItemUnionFilter(admin.SimpleListFilter):
    title = _("Forening")
    parameter_name = "union__calculated"

    def lookups(self, request: Any, model_admin: Any):
        queryset, filtervalue = get_filtered_emailitem_queryset(
            request, excluded_parameters={self.parameter_name}
        )

        union_ids = set(
            queryset.filter(department__union__isnull=False).values_list(
                "department__union__id", flat=True
            )
        )
        union_ids.update(
            queryset.filter(activity__department__union__isnull=False).values_list(
                "activity__department__union__id", flat=True
            )
        )

        if filtervalue is not None:
            self.title = f"Forening ({filtervalue})"

        accessible_unions = AdminUserInformation.get_unions_admin(request.user)
        unions = [
            (str(union.pk), union.name)
            for union in accessible_unions.filter(id__in=union_ids).order_by("name")
        ]

        if len(unions) <= 1:
            return ()

        return unions

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(department__union_id=self.value())
                | Q(activity__department__union_id=self.value())
            ).distinct()

        return queryset


class activityFilter(admin.SimpleListFilter):
    title = _("Aktivitet")
    parameter_name = "activity"

    def lookups(self, request: Any, model_admin: Any):
        queryset, filtervalue = get_filtered_emailitem_queryset(
            request, excluded_parameters={self.parameter_name}
        )
        activities = (
            queryset.filter(activity__isnull=False)
            .values_list("activity", flat=True)
            .distinct()
        )

        if filtervalue is not None:
            self.title = f"Aktivitet ({filtervalue})"

        activityList = [("none", "(Ingen aktivitet)")]
        for activity in (
            Activity.objects.filter(
                id__in=activities,
                department__in=AdminUserInformation.get_departments_admin(request.user),
            )
            .select_related("department")
            .order_by("department__name", "-start_date", "name")
        ):
            activityList.append(
                (
                    str(activity.id),
                    f"{activity.department.name} - {activity.name} [{activity.start_date:%Y-%m-%d} → {activity.end_date:%Y-%m-%d}]",
                )
            )

        if len(activityList) <= 2:
            return ()

        return activityList

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(activity__isnull=True).distinct()
        if self.value():
            return queryset.filter(activity=self.value()).order_by("activity__name")
        return queryset.order_by("activity__name")


class EmailItemDepartmentFilter(admin.SimpleListFilter):
    title = _("Afdeling")
    parameter_name = "department__calculated"

    def lookups(self, request: Any, model_admin: Any):
        queryset, filtervalue = get_filtered_emailitem_queryset(
            request, excluded_parameters={self.parameter_name}
        )

        department_ids = set(
            queryset.filter(department__isnull=False).values_list(
                "department__id", flat=True
            )
        )
        department_ids.update(
            queryset.filter(activity__department__isnull=False).values_list(
                "activity__department__id", flat=True
            )
        )

        if filtervalue is not None:
            self.title = f"Afdeling ({filtervalue})"

        accessible_departments = AdminUserInformation.get_departments_admin(
            request.user
        )
        departments = [
            (str(department.id), str(department.name))
            for department in accessible_departments.filter(
                id__in=department_ids
            ).order_by("name")
        ]

        if len(departments) <= 1:
            return ()

        return departments

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(department_id=self.value()) | Q(activity__department_id=self.value())
            ).distinct()

        return queryset


class EmailItemAdmin(admin.ModelAdmin):
    list_per_page = settings.LIST_PER_PAGE

    list_display = [
        "id",
        "created_dtm",
        "receiver",
        "departmentName",
        "activityName",
        "subject",
    ]

    list_filter = [
        EmailItemUnionFilter,
        EmailItemDepartmentFilter,
        activityFilter,
    ]

    date_hierarchy = "created_dtm"
    search_fields = (
        "person__name",
        "family__email",
        "activity__name",
        "subject",
    )
    search_help_text = mark_safe(
        "Du kan søge på personnavn, familie-email, afdelingsnavn, aktivitetsnavn eller email emne.<br>Vandret dato-filter er for hvornår emailen er oprettet"
    )
    readonly_fields = ("created_dtm", "send_error", "sent_dtm")
    autocomplete_fields = ("person", "family", "activity", "department")

    def get_queryset(self, request):
        return get_emailitem_queryset_for_user(request)

    fieldsets = [
        (
            "Modtager information",
            {
                "description": "Information om modtager (navn, familie, email)",
                "fields": (
                    "person",
                    "receiver",
                    "family",
                ),
            },
        ),
        (
            "Email information",
            {
                "description": "Indhold i email",
                "fields": (
                    "created_dtm",
                    "subject",
                    "body_text",
                    "body_html",
                ),
            },
        ),
        (
            "Yderlige data",
            {
                "description": "Diverse information om denne email",
                "fields": (
                    "template",
                    "bounce_token",
                    "activity",
                    "department",
                    "sent_dtm",
                    "send_error",
                ),
                "classes": ("collapse",),
            },
        ),
    ]


def getRequestDateFilter(request, date_type, queryset, filtervalue):
    if date_type in request.GET:
        date_part = request.GET[date_type]
        if date_type != "created_dtm__year":
            if len(date_part) == 1:
                date_part = f"0{date_part}"

        if filtervalue is None:
            filtervalue = date_part
        else:
            filtervalue += "-" + date_part

        kwargs = {f"{date_type}": date_part}

        return [queryset.filter(**kwargs), filtervalue]
    return [queryset, filtervalue]
