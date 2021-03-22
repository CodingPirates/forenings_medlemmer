from uuid import uuid4
from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html
from django.forms import Textarea

from members.models import (
    Address,
    AdminUserInformation,
    Person,
    Department,
    Union,
    Volunteer,
    Member,
    Activity,
    ActivityType,
    ActivityInvite,
    ActivityParticipant,
    Family,
    EmailItem,
    Payment,
    Equipment,
    EquipmentLoan,
    EmailTemplate,
)

from .address_admin import AddressAdmin
from .department_admin import DepartmentAdmin
from .union_admin import UnionAdmin
from .user_admin import UserAdmin
from .person_admin import PersonAdmin
from .member_admin import MemberAdmin
from .payment_admin import PaymentAdmin
from .activity_admin import ActivityAdmin

admin.site.site_header = "Coding Pirates Medlemsdatabase"
admin.site.index_title = "Afdelings admin"

admin.site.register(Address, AddressAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Union, UnionAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityType)
admin.site.register(EmailTemplate)


class EmailItemInline(admin.TabularInline):
    model = EmailItem
    fields = ["reciever", "subject", "sent_dtm"]
    can_delete = False
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    extra = 0


class PersonInline(admin.TabularInline):
    def admin_link(self, instance):
        url = reverse(
            "admin:%s_%s_change"
            % (instance._meta.app_label, instance._meta.model_name),
            args=(instance.id,),
        )
        return format_html('<a href="{}">{}</a>', url, instance.name)

    admin_link.short_description = "Navn"

    model = Person
    fields = ("admin_link", "membertype", "zipcode", "added", "notes")
    readonly_fields = fields
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
        departments = Department.objects.filter(adminuserinformation__user=request.user)
        return qs.filter(
            activity__end_date__gt=timezone.now(), activity__department__in=departments
        )


class MemberInline(admin.TabularInline):
    fields = ["department", "member_since", "member_until"]
    readonly_fields = fields
    model = Member
    extra = 0


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

    fields = ("email", "dont_send_mails", "confirmed_dtm")
    readonly_fields = ("confirmed_dtm",)
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
        if request.user.is_superuser:
            return qs
        departments = Department.objects.filter(
            adminuserinformation__user=request.user
        ).values("id")
        return qs.filter(
            Q(person__member__activityparticipant__activity__department__in=departments)
            | Q(person__waitinglist__department__in=departments)
            | Q(person__activityinvite__activity__department__in=departments)
        ).distinct()


admin.site.register(Family, FamilyAdmin)


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
                payment__isnull=False, payment__accepted_dtm__isnull=False
            )
        elif self.value() == "confirmed":
            return queryset.filter(
                payment__isnull=False, payment__confirmed_dtm__isnull=False
            )
        elif self.value() == "pending":
            return queryset.filter(
                payment__isnull=False, payment__confirmed_dtm__isnull=True
            )
        elif self.value() == "rejected":
            return queryset.filter(
                payment__isnull=False, payment__rejected_dtm__isnull=False
            )


class ActivityParticipantListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Efter aktivitet"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for activity in Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user)
        ).order_by("department__name", "-start_date"):
            activitys.append((str(activity.pk), str(activity)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity=self.value())


class ActivityParticipantAdmin(admin.ModelAdmin):
    list_display = [
        "added_dtm",
        "member",
        "person_age_years",
        "photo_permission",
        "activity",
        "note",
    ]
    list_filter = (ActivityParticipantListFilter, ParticipantPaymentListFilter)
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


admin.site.register(ActivityParticipant, ActivityParticipantAdmin)


class ActivityInviteAdminForm(forms.ModelForm):
    class Meta:
        model = ActivityInvite
        exclude = []

    def __init__(self, *args, **kwds):
        super(ActivityInviteAdminForm, self).__init__(*args, **kwds)
        self.fields["person"].queryset = Person.objects.order_by(Lower("name"))


class ActivivtyInviteActivityListFilter(admin.SimpleListFilter):
    title = "Aktiviteter"
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for activity in Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user)
        ).order_by("department__name"):
            activitys.append((str(activity.pk), activity))

        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__pk=self.value())


class ActivityInviteAdmin(admin.ModelAdmin):
    list_display = (
        "person",
        "activity",
        "invite_dtm",
        "person_age_years",
        "person_zipcode",
        "rejected_dtm",
    )
    list_filter = (ActivivtyInviteActivityListFilter,)
    search_fields = ("person__name",)
    list_display_links = None
    form = ActivityInviteAdminForm

    # Only show invitation to own activities
    def get_queryset(self, request):
        qs = super(ActivityInviteAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(activity__department__adminuserinformation__user=request.user)

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
                    "rejected_dtm",
                ),
            },
        ),
    )

    # Limit the activity possible to invite to: Not finished and belonging to user
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "activity" and not request.user.is_superuser:
            departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )
            kwargs["queryset"] = Activity.objects.filter(
                end_date__gt=timezone.now(), department__in=departments
            )
        return super(ActivityInviteAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def person_age_years(self, item):
        return item.person.age_years()

    person_age_years.short_description = "Alder"

    def person_zipcode(self, item):
        return item.person.zipcode

    person_zipcode.short_description = "Postnummer"


admin.site.register(ActivityInvite, ActivityInviteAdmin)


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


class EquipmentAdmin(admin.ModelAdmin):
    list_filter = ["department", "union"]
    list_display = ["title", "count", "union", "department"]
    search_fields = ("title", "notes")
    raw_id_fields = ("department", "union")
    inlines = (EquipmentLoanInline,)
    list_per_page = 20


# class AdminUserInformationAdmin(admin.ModelAdmin):
#    raw_id_fields = ("person",)

# admin.site.register(AdminUserInformation, AdminUserInformationAdmin)


admin.site.register(Equipment, EquipmentAdmin)
