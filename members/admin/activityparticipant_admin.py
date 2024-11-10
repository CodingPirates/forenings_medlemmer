from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.html import escape

from members.models import (
    Activity,
    AdminUserInformation,
    Union,
)

from members.admin.admin_actions import AdminActions


class ActivityParticipantDepartmentFilter(admin.SimpleListFilter):
    title = "Afdeling"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        return [
            (str(department.pk), str(department))
            for department in AdminUserInformation.get_departments_admin(
                request.user
            ).order_by("name")
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
    parameter_name = "activity_current_year"

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
    parameter_name = "activity_last_year"

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
    parameter_name = "activity_old_years"

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
    parameter_name = "department__union"

    def lookups(self, request, model_admin):
        unions = []
        for union1 in (
            Union.objects.filter(
                department__union__in=AdminUserInformation.get_unions_admin(
                    request.user
                )
            )
            .order_by("name")
            .distinct()
        ):
            unions.append((str(union1.pk), str(union1.name)))
        return unions

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__department__union__pk=self.value())


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
        "activity_link",
        "added_at",
        "activity_person_link",
        "activity_person_gender",
        "person_age_years",
        "photo_permission",
        "note",
        "activity_payment_info_html",
        "activity_family_email_link",
        "person_zipcode",
        "activity_activitytype",
        "activity_department_link",
    ]

    list_filter = (
        ActivityParticipantUnionFilter,
        ActivityParticipantDepartmentFilter,
        ActivityParticipantListCurrentYearFilter,
        ActivityParticipantListLastYearFilter,
        ActivityParticipantListOldYearsFilter,
        ParticipantPaymentListFilter,
        "activity__activitytype",
    )
    list_display_links = (
        "added_at",
        "photo_permission",
        "note",
    )
    date_hierarchy = "activity__start_date"
    raw_id_fields = ("activity",)
    search_fields = (
        "person__name",
        "activity__name",
    )

    actions = [
        AdminActions.invite_many_to_activity_action,
        AdminActions.export_participants_csv,
    ]

    def activity_activitytype(self, item):
        return item.activity.activitytype

    activity_activitytype.short_description = "Aktivitetstype"
    activity_activitytype.admin_order_field = "activity__activitytype"

    def person_age_years(self, item):
        return item.person.age_years()

    person_age_years.short_description = "Alder"
    person_age_years.admin_order_field = "-person__birthday"

    def person_zipcode(self, item):
        return item.person.zipcode

    person_zipcode.short_description = "Postnummer"

    # Only show participants to own departments
    def get_queryset(self, request):
        qs = super(ActivityParticipantAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
            return qs
        return qs.filter(activity__department__adminuserinformation__user=request.user)

    def activity_person_gender(self, item):
        return item.person.gender_text()

    activity_person_gender.short_description = "Køn"

    def activity_person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.person_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.person.name))
        return mark_safe(link)

    activity_person_link.short_description = "Deltager"
    activity_person_link.admin_order_field = "person__name"

    def activity_family_email_link(self, item):
        url = reverse("admin:members_family_change", args=[item.person.family_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.person.family.email))
        return mark_safe(link)

    activity_family_email_link.short_description = "Familie"
    activity_family_email_link.admin_order_field = "person__family__email"

    def activity_link(self, item):
        url = reverse("admin:members_activity_change", args=[item.activity.id])
        link = '<a href="%s">%s</a>' % (url, escape(item.activity.name))
        return mark_safe(link)

    activity_link.short_description = "Aktivitet"
    activity_link.admin_order_field = "activity__name"

    def activity_department_link(self, item):
        url = reverse(
            "admin:members_department_change", args=[item.activity.department_id]
        )
        link = '<a href="%s">%s</a>' % (url, escape(item.activity.department.name))
        return mark_safe(link)

    activity_department_link.short_description = "Afdeling"
    activity_department_link.admin_order_field = "activity__department__name"

    def activity_payment_info_txt(self, item):
        return item.payment_info(False)

    activity_payment_info_txt.short_description = "Betalingsinfo"

    def activity_payment_info_html(self, item):
        return item.payment_info(True)

    activity_payment_info_html.short_description = "Betalingsinfo"
