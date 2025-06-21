import codecs
from datetime import timedelta
from django.contrib import admin
from django.db.models import Max, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from members.models import AnonymizationCandidate, ActivityParticipant

from .person_admin import PersonAdmin


class AnonymizationCandidatesAdmin(PersonAdmin):
    """
    Admin view for showing persons who are candidates for being anonymized.
    Inherits from PersonAdmin to reuse existing functionality.
    """

    # Custom list display with requested columns
    list_display = (
        'name',
        'membertype',
        'gender_text',
        'family_url',
        'age_years',
        'is_candidate',
        'latest_activity',
        'last_login',
        'created_date',
    )

    # Keep existing filters but add focus on non-anonymized
    list_filter = (
        'membertype',
        'gender',
        'family__confirmed_at',  # To help identify old/inactive families
    )

    # Custom actions for this view
    actions = [
        'export_anonymization_candidates_csv',
        'anonymize_persons',  # Reuse existing anonymization action
    ]

    # Override title and description
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # extra_context['title'] = 'Anonymiserings kandidater'
        return super().changelist_view(request, extra_context)

    def get_actions(self, request):
        """
        Remove the delete action from available actions.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        """
        Override to show only non-anonymized persons who might be candidates for anonymization.
        This could include persons who haven't been active recently, etc.
        """
        qs = super().get_queryset(request)
        # Show only non-anonymized persons
        return qs.filter(anonymized=False)

    def is_candidate(self, obj):
        """
        Wrapper method to call the model's is_anonymization_candidate method.
        """
        return obj.is_anonymization_candidate()

    is_candidate.boolean = True
    is_candidate.short_description = 'Kan anonymiseres?'

    def created_date(self, obj):
        """
        Return the date when the person was created in the system.
        """
        return obj.added_at.strftime('%Y-%m-%d') if obj.added_at else 'Ukendt'

    created_date.short_description = 'Oprettet'
    created_date.admin_order_field = 'added_at'

    def latest_activity(self, obj):
        """
        Get the latest activity participation for this person.
        """
        latest_participation = ActivityParticipant.objects.filter(
            person=obj
        ).select_related('activity').order_by('-activity__end_date').first()

        if latest_participation:
            activity = latest_participation.activity
            activity_text = f"{activity.name} ({activity.end_date.strftime('%Y-%m-%d') if activity.end_date else 'Ingen slutdato'})"
            return format_html(
                '<a href="../activity/{}">{}</a>',
                activity.id,
                activity_text
            )
        return 'Ingen'

    latest_activity.short_description = 'Seneste aktivitet'
    latest_activity.admin_order_field = 'activityparticipant__activity__end_date'

    def last_login(self, obj):
        """
        Get the last login date for this person's associated user account.
        """
        if obj.user and obj.user.last_login:
            return obj.user.last_login.strftime('%Y-%m-%d %H:%M')
        return 'Aldrig'

    last_login.short_description = 'Seneste login'
    last_login.admin_order_field = 'user__last_login'

    def export_anonymization_candidates_csv(self, request, queryset):
        """
        Export the selected anonymization candidates to CSV.
        """
        result_string = "Name;Type;Køn;Familie;Alder;Kan anonymiseres?;Seneste aktivitet;Seneste login;Oprettet\n"

        for person in queryset:
            # Get latest activity info
            latest_participation = ActivityParticipant.objects.filter(
                person=person
            ).select_related('activity').order_by('-activity__end_date').first()

            if latest_participation:
                latest_activity_str = f"{latest_participation.activity.name} ({latest_participation.activity.end_date.strftime('%Y-%m-%d') if latest_participation.activity.end_date else 'No end date'})"
            else:
                latest_activity_str = "Ingen"

            # Get last login info
            if person.user and person.user.last_login:
                last_login_str = person.user.last_login.strftime('%Y-%m-%d %H:%M')
            else:
                last_login_str = "Aldrig"

            # Use model method for is_candidate
            is_candidate_str = "Ja" if person.is_anonymization_candidate() else "Nej"

            # Get created date
            created_date_str = person.added_at.strftime('%Y-%m-%d') if person.added_at else 'Ukendt'

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
                f'"{latest_activity_escaped}";'
                f'"{last_login_str}";'
                f'"{created_date_str}"\n'
            )

        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("utf-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="anonymiserings_kandidater.csv"'
        return response

    export_anonymization_candidates_csv.short_description = "Eksporter til CSV"
