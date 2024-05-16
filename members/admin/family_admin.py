from uuid import uuid4
from django.contrib import admin
from django.db.models import Q

from members.models import Department

from .inlines import (
    EmailItemInline,
    PersonInline,
    PaymentInline,
)


class FamilyAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        if request.user.has_perm("members.view_family_unique"):
            return ("email", "unique")
        else:
            return ("email",)

    search_fields = ("email",)

    inlines = [PersonInline, PaymentInline, EmailItemInline]
    actions = [
        "create_new_uuid",
        "resend_link_email",
    ]  # new UUID gets used accidentially
    # actions = ['resend_link_email']

    fields = ("email", "dont_send_mails", "confirmed_at")
    readonly_fields = ("confirmed_at",)
    list_per_page = 20

    def create_new_uuid(self, request, queryset):
        for family in queryset:
            family.unique = uuid4()
            family.save()
        if queryset.count() == 1:
            message_bit = "1 familie"
        else:
            message_bit = "%s familier" % queryset.count()
        self.message_user(request, "%s fik nyt UUID." % message_bit)

    create_new_uuid.short_description = "Generer nyt password"

    def resend_link_email(self, request, queryset):
        for family in queryset:
            family.send_link_email()
        if queryset.count() == 1:
            message_bit = "1 familie"
        else:
            message_bit = "%s familier" % queryset.count()
        self.message_user(request, "%s fik fik tilsendt link e-mail." % message_bit)

    resend_link_email.short_description = "Gensend link e-mail"

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
