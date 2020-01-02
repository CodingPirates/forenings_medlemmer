from uuid import uuid4
from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import Q
from members.models.person import Person
from members.models.department import Department
from members.models.union import Union
from members.models.member import Member
from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models.family import Family
from members.models.emailitem import EmailItem
from members.models.emailtemplate import EmailTemplate
from members.models.payment import Payment
from members.models.equipment import Equipment
from members.models.equipmentloan import EquipmentLoan
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html
from django.forms import Textarea
from members.models import Address

from .address_admin import AddressAdmin
from .department_admin import DepartmentAdmin
from .union_admin import UnionAdmin
from .user_admin import UserAdmin
from .person_admin import PersonAdmin

from .inlines import PaymentInline


admin.site.site_header = "Coding Pirates Medlemsdatabase"
admin.site.index_title = "Afdelings admin"

admin.site.register(Address, AddressAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Union, UnionAdmin)
admin.site.register(Person, PersonAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


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


class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "member_since", "is_active")
    list_filter = ["department"]
    list_per_page = 20
    raw_id_fields = ("department", "person")

    # Only view mebers related to users department
    def get_queryset(self, request):
        qs = super(MemberAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        departments = Department.objects.filter(
            adminuserinformation__user=request.user
        ).values("id")
        return qs.filter(
            activityparticipant__activity__department__in=departments
        ).distinct()


admin.site.register(Member, MemberAdmin)


class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "department",
        "start_date",
        "open_invite",
        "price_in_dkk",
        "max_participants",
    )
    date_hierarchy = "start_date"
    search_fields = ("name", "department__name")
    list_per_page = 20
    raw_id_fields = ("department",)
    # list_filter = ('department','open_invite')

    # Only view activities on own department
    def get_queryset(self, request):
        qs = super(ActivityAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        departments = Department.objects.filter(adminuserinformation__user=request.user)
        return qs.filter(department__in=departments)

    # Only show own departments when creating new activity
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department" and not request.user.is_superuser:
            kwargs["queryset"] = Department.objects.filter(
                adminuserinformation__user=request.user
            )
        return super(ActivityAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    fieldsets = (
        ("Afdeling", {"fields": ("department",)}),
        (
            "Aktivitet",
            {
                "description": "<p>Aktivitetsnavnet skal afspejle aktivitet samt tidspunkt. F.eks. <em>Forårssæson 2018</em>.</p><p>Tidspunkt er f.eks. <em>Onsdage 17:00-19:00</em></p>",
                "fields": (
                    "name",
                    "open_hours",
                    "description",
                    "start_date",
                    "end_date",
                    "member_justified",
                ),
            },
        ),
        (
            "Lokation og ansvarlig",
            {
                "description": "<p>Adresse samt ansvarlig kan adskille sig fra afdelingens informationer (f.eks. et gamejam der foregår et andet sted).</p>",
                "fields": (
                    "responsible_name",
                    "responsible_contact",
                    "streetname",
                    "housenumber",
                    "floor",
                    "door",
                    "zipcode",
                    "city",
                    "placename",
                ),
            },
        ),
        (
            "Tilmeldingsdetaljer",
            {
                "description": '<p>Tilmeldingsinstruktioner er tekst der kommer til at stå på betalingsformularen på tilmeldingssiden. Den skal bruges til at stille spørgsmål, som den, der tilmelder sig, kan besvare ved tilmelding.</p><p>Fri tilmelding betyder, at alle, når som helst kan tilmelde sig denne aktivitet - efter "først til mølle"-princippet. Dette er kun til arrangementer og klubaften-sæsoner i områder, hvor der ikke er nogen venteliste. Alle arrangementer med fri tilmelding kommer til at stå med en stor "tilmeld" knap på medlemssiden. <b>Vi bruger typisk ikke fri tilmelding - spørg i Slack hvis du er i tvivl!</b></p>',
                "fields": (
                    "instructions",
                    "open_invite",
                    "price_in_dkk",
                    "signup_closing",
                    "max_participants",
                    "min_age",
                    "max_age",
                ),
            },
        ),
    )


admin.site.register(Activity, ActivityAdmin)


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
            ("none", "Ikke betalt"),
            ("ok", "Betalt"),
            ("confirmed", "Hævet"),
            ("pending", "Afventende"),
            ("rejected", "Afvist"),
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
        if request.user.is_superuser:
            departments = Department.objects.filter()
        else:
            departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )

        for activity in (
            Activity.objects.filter(department__in=departments)
            .order_by("start_date")
            .order_by("zipcode")
        ):
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
    # Title shown in filter view
    title = "Aktiviteter"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            departments = Department.objects.filter()
        else:
            departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )

        activitys = []
        for activity in Activity.objects.filter(department__in=departments).order_by(
            "zipcode"
        ):
            activitys.append((str(activity.pk), activity))

        return activitys

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

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


class PersonWaitinglistListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Venteliste"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "waiting_list"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            department_queryset = Department.objects.filter(
                has_waiting_list=True
            ).order_by("zipcode")
        else:
            department_queryset = Department.objects.filter(
                has_waiting_list=True, adminuserinformation__user=request.user
            ).order_by("zipcode")

        departments = [
            ("any", "Alle opskrevne samlet"),
            ("none", "Ikke skrevet på venteliste"),
        ]
        for department in department_queryset:
            departments.append((str(department.pk), department.name))

        return departments

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        if self.value() == "any":
            return queryset.exclude(waitinglist__isnull=True)
        elif self.value() == "none":
            return queryset.filter(waitinglist__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(waitinglist__department__pk=self.value())


admin.site.register(EmailTemplate)


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "added",
        "payment_type",
        "amount_ore",
        "family",
        "confirmed_dtm",
        "cancelled_dtm",
        "rejected_dtm",
        "activityparticipant",
    ]
    list_filter = ["payment_type", "activity"]
    raw_id_fields = ("person", "activityparticipant", "family")
    date_hierarchy = "added"
    search_fields = ("family__email",)
    select_related = "activityparticipant"


admin.site.register(Payment, PaymentAdmin)
# admin.site.register(QuickpayTransaction)


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
