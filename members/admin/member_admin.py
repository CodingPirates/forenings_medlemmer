from django.contrib import admin

from members.models import Department, AdminUserInformation


class DepartmentFilter(admin.SimpleListFilter):
    title = "Afdeling"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        return [
            (str(department.pk), department.name)
            for department in AdminUserInformation.get_departments_admin(
                request.user
            ).order_by("name")
        ]

    def queryset(self, request, queryset):
        return (
            queryset
            if self.value() is None
            else queryset.filter(department__pk=self.value())
        )


class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "member_since", "is_active")
    list_filter = [DepartmentFilter]
    list_per_page = 20
    raw_id_fields = ("department", "person")

    # Only view mebers related to users department
    def get_queryset(self, request):
        qs = super(MemberAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        departments = Department.objects.filter(
            adminuserinformation__user=request.user
        ).values("id")
        return qs.filter(
            activityparticipant__activity__department__in=departments
        ).distinct()
