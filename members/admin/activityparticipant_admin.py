import codecs
from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

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
        "activity_department_link",
        "activity_link",
        "added_at",
        "activity_person_link",
        "activity_person_gender",
        "person_age_years",
        "activity_family_email_link",
        "person_zipcode",
        "photo_permission",
        "note",
        "activity_payment_info_html",
        "activity_union_link",
    ]

    list_filter = (
        ActivityParticipantUnionFilter,
        ActivityParticipantDepartmentFilter,
        ActivityParticipantListCurrentYearFilter,
        ActivityParticipantListLastYearFilter,
        ActivityParticipantListOldYearsFilter,
        ParticipantPaymentListFilter,
    )
    list_display_links = (
        "added_at",
        "photo_permission",
        "note",
    )
    date_hierarchy = "activity__start_date"
    raw_id_fields = ("activity",)
    search_fields = (
        "member__person__name",
        "activity__name",
    )

    actions = [
        "export_csv_full",
    ]

    def person_age_years(self, item):
        return item.member.person.age_years()

    person_age_years.short_description = "Alder"
    person_age_years.admin_order_field = "-member__person__birthday"

    def person_zipcode(self, item):
        return item.member.person.zipcode

    person_zipcode.short_description = "Postnummer"

    # Only show participants to own departments
    def get_queryset(self, request):
        qs = super(ActivityParticipantAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(activity__department__adminuserinformation__user=request.user)

    def activity_person_gender(self, item):
        if item.member.person.gender == "MA":
            return "Dreng"
        elif item.member.person.gender == "FM":
            return "Pige"
        else:
            return "Andet"

    activity_person_gender.short_description = "Køn"

    def activity_person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.member.person_id])
        link = '<a href="%s">%s</a>' % (url, item.member.person.name)
        return mark_safe(link)

    activity_person_link.short_description = "Deltager"
    activity_person_link.admin_order_field = "member__person__name"

    def activity_family_email_link(self, item):
        url = reverse(
            "admin:members_family_change", args=[item.member.person.family_id]
        )
        link = '<a href="%s">%s</a>' % (url, item.member.person.family.email)
        return mark_safe(link)

    activity_family_email_link.short_description = "Familie"
    activity_family_email_link.admin_order_field = "member__person__family__email"

    def activity_link(self, item):
        url = reverse("admin:members_activity_change", args=[item.activity.id])
        link = '<a href="%s">%s</a>' % (url, item.activity.name)
        return mark_safe(link)

    activity_link.short_description = "Aktivitet"
    activity_link.admin_order_field = "activity__name"

    def activity_union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.activity.union_id])
        link = '<a href="%s">%s</a>' % (url, item.activity.union.name)
        return mark_safe(link)

    activity_union_link.short_description = (
        "Forening for Foreningsmedlemskab/Støttemedlemskab"
    )
    activity_union_link.admin_order_field = "activity__union__name"

    def activity_department_link(self, item):
        url = reverse(
            "admin:members_department_change", args=[item.activity.department_id]
        )
        link = '<a href="%s">%s</a>' % (url, item.activity.department.name)
        return mark_safe(link)

    activity_department_link.short_description = "Afdeling"
    activity_department_link.admin_order_field = "activity__department__name"

    def activity_payment_info_txt(self, item):
        if item.activity.price_in_dkk == 0.00:
            return "Gratis"
        else:
            try:
                return item.payment_info(False)
            except Exception:
                return "Andet er aftalt"

    activity_payment_info_txt.short_description = "Betalingsinfo"

    def activity_payment_info_html(self, item):
        if item.activity.price_in_dkk == 0.00:
            return format_html("<span style='color:green'><b>Gratis</b></span>")
        else:
            try:
                return item.payment_info(True)
            except Exception:
                return format_html(
                    "<span style='color:red'><b>Andet er aftalt</b></span>"
                )

    activity_payment_info_html.short_description = "Betalingsinfo"

    def export_csv_full(self, request, queryset):
        result_string = "Forening;Afdeling;Aktivitet;Navn;Alder;"
        result_string += "Køn;Post-nr;Betalingsinfo;Forældre navn;Forældre email;"
        result_string += "Forældre tlf;Note til arrangørerne\n"
        for p in queryset:
            if p.member.person.gender == "MA":
                gender = "Dreng"
            elif p.member.person.gender == "FM":
                gender = "Pige"
            else:
                gender = p.member.person.gender

            parent = p.member.person.family.get_first_parent()
            if parent:
                parent_name = parent.name
                parent_phone = parent.phone
                if not p.member.person.family.dont_send_mails:
                    parent_email = parent.email
                else:
                    parent_email = ""
            else:
                parent_name = ""
                parent_phone = ""
                parent_email = ""

            result_string = (
                result_string
                + p.activity.department.union.name
                + ";"
                + p.activity.department.name
                + ";"
                + p.activity.name
                + ";"
                + p.member.person.name
                + ";"
                + str(p.member.person.age_years())
                + ";"
                + gender
                + ";"
                + p.member.person.zipcode
                + ";"
                + self.activity_payment_info_txt(p)
                + ";"
                + parent_name
                + ";"
                + parent_email
                + ";"
                + parent_phone
                + ";"
                + '"'
                + p.note.replace('"', '""')
                + '"'
                + "\n"
            )
        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("utf-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="deltagere.csv"'
        return response

    export_csv_full.short_description = "CSV Export"
