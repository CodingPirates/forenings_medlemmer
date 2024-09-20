from django.contrib import admin

from members.models import (
    Department,
    AdminUserInformation,
)


class VolunteerRequestDepartmentListFilter(admin.SimpleListFilter):
    title = "Afdelinger"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        departments = []
        for d in (
            Department.objects.filter(
                volunteerrequestdepartment__department__in=AdminUserInformation.get_departments_admin(
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
            return queryset.filter(department__pk=self.value)


class VolunteerRequestDepartmentAdmin(admin.ModelAdmin):
    list_display = ("volunteer_request", "department", "created", "finished", "status")

    date_hierarchy = "created"
    readonly_fields = ("whishes", "reference")

    list_filter = (
        VolunteerRequestDepartmentListFilter,
        "status",
    )

    fieldsets = [
        (
            "Forespørgsel",
            {
                "description": "Information fra person om at blive frivillig",
                "fields": (
                    "volunteer_request",
                    "department",
                    "whishes",
                    "reference",
                ),
            },
        ),
        (
            "Dato og status",
            {
                "description": "Information om oprettelse og status",
                "fields": ("created", "finished", "status"),
            },
        ),
    ]
