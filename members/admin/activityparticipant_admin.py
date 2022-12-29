from django.contrib import admin
from django.utils import timezone

from members.models import (
    Activity,
    AdminUserInformation,
    Department,
    Union,
)


class ActivityParticipantDepartmentFilter(admin.SimpleListFilter):
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


class ActivityParticipantListCurrentYearFilter(admin.SimpleListFilter):
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


class ActivityParticipantListLastYearFilter(admin.SimpleListFilter):
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


class ActivityParticipantListOldYearsFilter(admin.SimpleListFilter):
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


class ActivityParticipantUnionFilter(admin.SimpleListFilter):
    title = "Lokalforening"
    parameter_name = "union"

    def lookups(self, request, model_admin):
        return [(str(union.pk), str(union.name)) for union in Union.objects.all()]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__union__pk=self.value())


class ParticipantPaymentListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Betaling"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "payment_list"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        activitys = [
            ("pending", "Afventende"),
            ("rejected", "Afvist"),
            ("ok", "Betalt"),
            ("none", "Ikke betalt"),
            ("confirmed", "Hævet"),
        ]
        return activitys

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        if self.value() == "none":
            return queryset.filter(payment__isnull=True)
        elif self.value() == "ok":
            return queryset.filter(
                payment__isnull=False, payment__accepted_at__isnull=False
            )
        elif self.value() == "confirmed":
            return queryset.filter(
                payment__isnull=False, payment__confirmed_at__isnull=False
            )
        elif self.value() == "pending":
            return queryset.filter(
                payment__isnull=False, payment__confirmed_at__isnull=True
            )
        elif self.value() == "rejected":
            return queryset.filter(
                payment__isnull=False, payment__rejected_at__isnull=False
            )


class ActivityParticipantAdmin(admin.ModelAdmin):
    list_display = [
        "added_at",
        "member",
        "person_age_years",
        "photo_permission",
        "activity",
        "note",
    ]
    list_filter = (
        ActivityParticipantUnionFilter,
        ActivityParticipantDepartmentFilter,
        ActivityParticipantListCurrentYearFilter,
        ActivityParticipantListLastYearFilter,
        ActivityParticipantListOldYearsFilter,
        ParticipantPaymentListFilter,
    )
    list_display_links = ("member",)
    raw_id_fields = ("activity", "member")
    search_fields = ("member__person__name",)

    def person_age_years(self, item):
        return item.member.person.age_years()

    person_age_years.short_description = "Alder"
    person_age_years.admin_order_field = "-member__person__birthday"

    # Only show participants to own departments
    def get_queryset(self, request):
        qs = super(ActivityParticipantAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(activity__department__adminuserinformation__user=request.user)
