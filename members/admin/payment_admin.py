from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.urls import reverse


from members.models import Activity, AdminUserInformation, Department


class PaymentDepartmentFilter(admin.SimpleListFilter):
    title = "Afdeling"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        return [
            (str(department.pk), str(department))
            for department in Department.objects.all()
        ]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__department__pk=self.value())


class PaymentActivityCurrentYearAndFutureFilter(admin.SimpleListFilter):
    # Title shown in filter view. \u2265 : ≥ (større end eller lig med)
    title = "Efter aktivitet (\u2265 år " + str(timezone.now().year) + ")"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for act in Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user),
            start_date__year__gte=timezone.now().year,
        ).order_by("department__name", "-start_date"):
            activitys.append((str(act.pk), str(act)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity=self.value())


class PaymentActivityLastYearFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Efter aktivitet (= år " + str(timezone.now().year - 1) + ")"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for act in Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user),
            start_date__year=timezone.now().year - 1,
        ).order_by("department__name", "-start_date"):
            activitys.append((str(act.pk), str(act)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity=self.value())


class PaymentActivityOldYearsFilter(admin.SimpleListFilter):
    # Title shown in filter view. \u2264 : ≤ (mindre end eller lig med)
    title = "Efter aktivitet (\u2264 år " + str(timezone.now().year - 2) + ")"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for act in Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user),
            start_date__year__lte=timezone.now().year - 2,
        ).order_by("department__name", "-start_date"):
            activitys.append((str(act.pk), str(act)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity=self.value())


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "added_at",
        "payment_type",
        "amount_ore",
        "family_url",
        "confirmed_at",
        "cancelled_at",
        "rejected_at",
        "payment_person_link",
        "activity_link",
        "department_link",
    ]
    list_filter = [
        "payment_type",
        PaymentDepartmentFilter,
        PaymentActivityCurrentYearAndFutureFilter,
        PaymentActivityLastYearFilter,
        PaymentActivityOldYearsFilter,
    ]
    raw_id_fields = ("person", "activityparticipant", "family")
    date_hierarchy = "added_at"
    search_fields = ("family__email",)
    select_related = "activityparticipant"

    def family_url(self, item):
        return format_html(
            '<a href="../family/%d">%s</a>' % (item.family.id, item.family.email)
        )

    family_url.allow_tags = True
    family_url.short_description = "Familie"

    def payment_person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.person_id])
        link = '<a href="%s">%s</a>' % (url, item.person.name)
        return mark_safe(link)

    payment_person_link.short_description = "Deltager"
    payment_person_link.admin_order_field = "person__name"

    def department_link(self, item):
        url = reverse(
            "admin:members_department_change", args=[item.activity.department.id]
        )
        link = '<a href="%s">%s</a>' % (url, item.activity.department.name)
        return mark_safe(link)

    department_link.short_description = "Afdeling"
    department_link.admin_order_field = "activity__department__name"

    def activity_link(self, item):
        url = reverse("admin:members_activity_change", args=[item.activity.id])
        link = '<a href="%s">%s</a>' % (url, item.activity.name)
        return mark_safe(link)

    activity_link.short_description = "Aktivitet"
    activity_link.admin_order_field = "activity__name"
