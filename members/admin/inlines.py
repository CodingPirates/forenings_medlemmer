from django.contrib import admin
from django.utils import timezone

from members.models import (
    Activity,
    ActivityInvite,
    ActivityParticipant,
    AdminUserInformation,
    Department,
    Member,
    Payment,
    Volunteer,
    WaitingList,
)


class WaitingListInline(admin.TabularInline):
    model = WaitingList
    fields = ["on_waiting_list_since", "department", "number_on_waiting_list"]
    readonly_fields = fields
    extra = 0


class MemberInline(admin.TabularInline):
    fields = ["department", "member_since", "member_until"]
    readonly_fields = fields
    model = Member
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    fields = ("added", "payment_type", "confirmed_dtm", "rejected_dtm", "amount_ore")
    readonly_fields = ("family",)
    extra = 0


class VolunteerInline(admin.TabularInline):
    model = Volunteer
    fields = ("department", "added", "confirmed", "removed")
    extra = 0


class ActivityParticipantInline(admin.TabularInline):
    model = ActivityParticipant
    extra = 0

    def get_queryset(self, request):
        return ActivityParticipant.objects.all()


class ActivityInviteInline(admin.TabularInline):
    model = ActivityInvite
    extra = 0
    can_delete = False
    raw_id_fields = ("activity",)

    # Limit the activity possible to invite to: Not finished and belonging to user
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "activity" and not request.user.is_superuser:
            departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )
            kwargs["queryset"] = Activity.objects.filter(
                end_date__gt=timezone.now(), department__in=departments
            )
        return super(ActivityInviteInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    # Only view invites it would be possible for user to give out
    def get_queryset(self, request):
        qs = super(ActivityInviteInline, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            activity__end_date__gt=timezone.now(),
            activity__department__in=AdminUserInformation.get_departments_admin(
                request.user
            ),
        )
