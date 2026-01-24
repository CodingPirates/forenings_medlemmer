import codecs
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.urls import reverse

from members.models import ActivityParticipant

from .person_admin import PersonAdmin


class IsActiveFilter(admin.SimpleListFilter):
    title = "Aktiv"
    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Ja, seneste 2 år"),
            ("no", "Nej, ikke aktiv seneste 2 år"),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta, datetime
        from django.db.models import Q

        two_years_ago = timezone.now() - timedelta(days=2 * 365)
        today = timezone.now().date()
        # Calculate the correct "five full fiscal years" boundary
        five_full_fiscal_years = timezone.make_aware(datetime(today.year - 5, 1, 1))

        if self.value() == "no":
            # Show members that are anonymization candidates (no activity, login, or creation in last 2 years,
            # and no payment in last 5 full fiscal years)
            return (
                queryset.filter(
                    # Person was created at least 2 years ago
                    added_at__lt=two_years_ago
                )
                .filter(
                    # AND (no user OR user hasn't logged in within 2 years)
                    Q(user__isnull=True)
                    | Q(user__last_login__lt=two_years_ago)
                )
                .filter(
                    # AND (no activity participation OR latest activity was more than 2 years ago)
                    ~Q(
                        activityparticipant__activity__end_date__gte=two_years_ago.date()
                    )
                )
                .filter(
                    # AND no payment for person or family in last 5 full fiscal years
                    ~Q(payment__added_at__gte=five_full_fiscal_years)
                    & ~Q(family__payment__added_at__gte=five_full_fiscal_years)
                )
                .distinct()
            )

        elif self.value() == "yes":
            # Show members that are NOT anonymization candidates (recent activity, login, creation, or payment)
            return queryset.filter(
                Q(
                    # Person was created less than 2 years ago
                    added_at__gte=two_years_ago
                )
                | Q(
                    # OR user has logged in within 2 years
                    user__last_login__gte=two_years_ago
                )
                | Q(
                    # OR has activity participation within 2 years
                    activityparticipant__activity__end_date__gte=two_years_ago.date()
                )
                | Q(
                    # OR payment for person in last 5 full fiscal years
                    payment__added_at__gte=five_full_fiscal_years
                )
                | Q(
                    # OR payment for family in last 5 full fiscal years
                    family__payment__added_at__gte=five_full_fiscal_years
                )
            ).distinct()

        return queryset


class AnonymizationCandidatesAdmin(PersonAdmin):
    """
    Admin view for showing persons who are candidates for being anonymized.
    Inherits from PersonAdmin to reuse existing functionality.
    """

    list_per_page = settings.LIST_PER_PAGE

    # Custom list display with requested columns
    list_display = (
        "key_column",
        "person_link",
        "membertype",
        "gender_text",
        "family_link",
        "age_years",
        "last_active",
        "latest_activity",
        "last_login",
        "created_date",
    )

    # Filters for the anonymization candidates view
    list_filter = (
        "membertype",
        IsActiveFilter,
    )

    # Custom actions for this view
    actions = [
        "export_anonymization_candidates_csv",
        "anonymize_persons",
    ]

    def person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.id])
        link = '<a href="%s">%s</a>' % (url, escape(item.name))
        return mark_safe(link)

    person_link.short_description = "Person"
    person_link.admin_order_field = "name"

    # Override title and description
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        return super().changelist_view(request, extra_context)

    def get_actions(self, request):
        """
        Remove the delete action from available actions.
        """
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def get_queryset(self, request):
        """
        Override to show only non-anonymized persons who might be candidates for anonymization.
        This could include persons who haven't been active recently, etc.
        """
        qs = super().get_queryset(request)
        # Show only non-anonymized persons
        return qs.filter(anonymized=False)

    def has_add_permission(self, request):
        """
        Hide add button on admin view page
        """
        return False

    def last_active(self, obj):
        """
        Show the most recent date among created_date, latest_activity, and last_login.
        Color it red if person is candidate for anonymization, green otherwise.
        """
        dates = []

        # Add created date
        if obj.added_at:
            dates.append(obj.added_at.date())

        # Add latest activity end date
        latest_participation = (
            ActivityParticipant.objects.filter(person=obj)
            .select_related("activity")
            .order_by("-activity__end_date")
            .first()
        )

        if latest_participation and latest_participation.activity.end_date:
            dates.append(latest_participation.activity.end_date)

        # Add last login date
        if obj.user and obj.user.last_login:
            dates.append(obj.user.last_login.date())

        if not dates:
            date_str = "Aldrig"
        else:
            most_recent_date = max(dates)
            date_str = most_recent_date.strftime("%Y-%m-%d")

        # Color based on anonymization candidate status
        is_candidate = obj.is_anonymization_candidate()[0]
        color = "red" if is_candidate else "green"

        return format_html('<span style="color: {}">{}</span>', color, date_str)

    last_active.short_description = "Sidst aktiv"
    last_active.admin_order_field = "added_at"

    def created_date(self, obj):
        """
        Return the date when the person was created in the system.
        """
        return obj.added_at.strftime("%Y-%m-%d") if obj.added_at else "Ukendt"

    created_date.short_description = "Oprettet"
    created_date.admin_order_field = "added_at"

    def latest_activity(self, obj):
        """
        Get the latest activity participation for this person.
        """
        latest_participation = (
            ActivityParticipant.objects.filter(person=obj)
            .select_related("activity")
            .order_by("-activity__end_date")
            .first()
        )

        if latest_participation:
            activity = latest_participation.activity
            activity_text = f"{activity.name} ({activity.end_date.strftime('%Y-%m-%d') if activity.end_date else 'Ingen slutdato'})"
            return format_html(
                '<a href="../activity/{}">{}</a>', activity.id, activity_text
            )
        return "Ingen"

    latest_activity.short_description = "Senest tilmeldt"
    latest_activity.admin_order_field = "activityparticipant__activity__end_date"

    def last_login(self, obj):
        """
        Get the last login date for this person's associated user account.
        """
        if obj.user and obj.user.last_login:
            return obj.user.last_login.strftime("%Y-%m-%d")
        return "Aldrig"

    last_login.short_description = "Seneste login"
    last_login.admin_order_field = "user__last_login"

    def export_anonymization_candidates_csv(self, request, queryset):
        """
        Export the selected anonymization candidates to CSV.
        """
        result_string = "Name;Type;Køn;Familie;Alder;Kan anonymiseres?;Sidst aktiv;Seneste aktivitet;Seneste login;Oprettet\n"

        for person in queryset:
            # Get latest activity info
            latest_participation = (
                ActivityParticipant.objects.filter(person=person)
                .select_related("activity")
                .order_by("-activity__end_date")
                .first()
            )

            if latest_participation:
                latest_activity_str = f"{latest_participation.activity.name} ({latest_participation.activity.end_date.strftime('%Y-%m-%d') if latest_participation.activity.end_date else 'No end date'})"
            else:
                latest_activity_str = "Ingen"

            # Get last login info
            if person.user and person.user.last_login:
                last_login_str = person.user.last_login.strftime("%Y-%m-%d")
            else:
                last_login_str = "Aldrig"

            is_candidate_str = "Ja" if person.is_anonymization_candidate()[0] else "Nej"

            # Calculate last active date (same logic as in last_active method)
            dates = []
            if person.added_at:
                dates.append(person.added_at.date())
            if latest_participation and latest_participation.activity.end_date:
                dates.append(latest_participation.activity.end_date)
            if person.user and person.user.last_login:
                dates.append(person.user.last_login.date())

            if not dates:
                last_active_str = "Aldrig"
            else:
                most_recent_date = max(dates)
                last_active_str = most_recent_date.strftime("%Y-%m-%d")

            # Get created date
            created_date_str = (
                person.added_at.strftime("%Y-%m-%d") if person.added_at else "Ukendt"
            )

            # Get membertype display
            membertype_display = person.get_membertype_display()

            # Escape values for CSV
            name_escaped = person.name.replace('"', '""')
            family_email_escaped = person.family.email.replace('"', '""')
            latest_activity_escaped = latest_activity_str.replace('"', '""')

            result_string += (
                f'"{name_escaped}";'
                f'"{membertype_display}";'
                f'"{person.gender_text()}";'
                f'"{family_email_escaped}";'
                f'"{person.age_years()}";'
                f'"{is_candidate_str}";'
                f'"{last_active_str}";'
                f'"{latest_activity_escaped}";'
                f'"{last_login_str}";'
                f'"{created_date_str}"\n'
            )

        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("utf-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = (
            'attachment; filename="anonymiserings_kandidater.csv"'
        )
        return response

    export_anonymization_candidates_csv.short_description = "Eksporter til CSV"
