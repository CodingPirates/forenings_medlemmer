from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html

from members.models import Department

from .filters.common_filters import AnonymizedFilter
from .inlines import (
    EmailItemInline,
    PaymentInline,
    PersonInline,
)


class FamilyAdmin(admin.ModelAdmin):
    list_filter = (AnonymizedFilter,)

    def get_list_display(self, request):
        if request.user.has_perm("members.view_family_unique"):
            return ("id", "email", "unique")
        else:
            return (
                "id",
                "email",
            )

    search_fields = ("email",)

    inlines = [PersonInline, PaymentInline, EmailItemInline]
    list_per_page = settings.LIST_PER_PAGE
    fields = ("anonymization_status", "email", "dont_send_mails", "confirmed_at")
    readonly_fields = ("anonymization_status", "confirmed_at")

    @admin.display(description="Anonymisering")
    def anonymization_status(self, obj):
        if not obj or not obj.pk:
            return ""
        if obj.anonymized:
            return format_html(
                "<p><strong>Denne familie er anonymiseret.</strong> "
                "E-mail og andre personlige oplysninger er erstattet eller fjernet.</p>"
            )
        return "Denne familie er ikke anonymiseret."

    # Only view familys related to users department (via participant, waitinglist & invites)
    def get_queryset(self, request):
        qs = super(FamilyAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
            return qs
        departments = Department.objects.filter(
            adminuserinformation__user=request.user
        ).values("id")
        return qs.filter(
            Q(person__activityparticipant__activity__department__in=departments)
            | Q(person__waitinglist__department__in=departments)
            | Q(person__activityinvite__activity__department__in=departments)
        ).distinct()
