from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.urls import reverse
from django.utils.html import format_html

from members.models import (
    Activity,
    ActivityInvite,
    AdminUserInformation,
    Department,
    EmailItem,
    EquipmentLoan,
    Payment,
    Person,
    Volunteer,
    WaitingList,
)


class ActivityInviteInline(admin.TabularInline):
    model = ActivityInvite
    extra = 0
    can_delete = False
    raw_id_fields = ("activity",)

    fieldsets = (
        (
            None,
            {
                "description": '<p>Invitationer til en aktivitet laves nemmere via "person" oversigten. Gå derind og filtrer efter f.eks. børn på venteliste til din afdeling og sorter efter opskrivningsdato, eller filter medlemmer på forrige sæson. Herefter kan du vælge de personer på listen, du ønsker at invitere og vælge "Inviter alle valgte til en aktivitet" fra rullemenuen foroven.</p>',
                "fields": (
                    "person",
                    "activity",
                    "invite_dtm",
                    "expire_dtm",
                    "rejected_at",
                    "price_in_dkk",
                    "price_note",
                ),
            },
        ),
    )

    # Limit the activity possible to invite to: Not finished and belonging to user
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if (
            db_field.name == "activity"
            and not request.user.is_superuser
            and not request.user.has_perm("members.view_all_departments")
        ):
            departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )
            kwargs["queryset"] = Activity.objects.filter(department__in=departments)
        return super(ActivityInviteInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    # Only view invites it would be possible for user to give out
    def get_queryset(self, request):
        qs = super(ActivityInviteInline, self).get_queryset(request)
        return qs.filter(
            activity__department__in=AdminUserInformation.get_departments_admin(
                request.user
            ),
        )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "invite_dtm",
            ]
        else:
            return []


class EmailItemInline(admin.TabularInline):
    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    model = EmailItem
    classes = ["hideheader", "collapse"]
    fields = [
        "created_ymdhm",
        "sent_ymdhm_text",
        "receiver",
        "email_link",
    ]
    can_delete = False
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    extra = 0


class EquipmentLoanInline(admin.TabularInline):
    model = EquipmentLoan
    fields = (
        "count",
        "person",
        "department",
        "loaned_dtm",
        "expected_back_dtm",
        "returned_dtm",
        "note",
    )
    readonly_fields = ("loaned_dtm",)
    can_delete = False
    raw_id_fields = ("person",)
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 40})}
    }
    extra = 0


class PaymentInline(admin.TabularInline):
    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    classes = ["showheader"]
    model = Payment
    fields = ("added_at", "payment_type", "confirmed_at", "rejected_at", "amount_ore")
    readonly_fields = ("family",)
    extra = 0


class PersonInline(admin.TabularInline):
    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    def admin_link(self, instance):
        url = reverse(
            "admin:%s_%s_change"
            % (instance._meta.app_label, instance._meta.model_name),
            args=(instance.id,),
        )
        return format_html('<a href="{}">{}</a>', url, instance.name)

    admin_link.short_description = "Navn"

    model = Person
    fields = ("admin_link", "membertype", "zipcode", "added_at", "notes")
    readonly_fields = fields
    can_delete = False
    classes = ["hideheader"]
    extra = 0


class VolunteerInline(admin.TabularInline):
    model = Volunteer
    fields = ("department", "added_at", "confirmed", "removed")
    extra = 0


class WaitingListInline(admin.TabularInline):
    model = WaitingList
    fields = [
        "on_waiting_list_since",
        "department",
        "number_on_waiting_list",
        "added_at",
    ]
    readonly_fields = fields
    extra = 0
