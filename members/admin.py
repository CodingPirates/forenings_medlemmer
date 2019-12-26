from uuid import uuid4
from django import forms
from django.contrib import admin
from django.db import models
from django.db import transaction
from django.db.models import Q
from members.models.person import Person
from members.models.department import Department, AdminUserInformation
from members.models.union import Union
from members.models.volunteer import Volunteer
from members.models.member import Member
from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models.family import Family
from members.models.emailitem import EmailItem
from members.models.waitinglist import WaitingList
from members.models.emailtemplate import EmailTemplate
from members.models.payment import Payment
from members.models.equipment import Equipment
from members.models.equipmentloan import EquipmentLoan
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.utils.html import format_html
from django.forms import Textarea
from django.shortcuts import render
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib import messages

admin.site.site_header = "Coding Pirates Medlemsdatabase"
admin.site.index_title = "Afdelings admin"


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


class UnionAdmin(admin.ModelAdmin):
    list_filter = ("region",)
    fieldsets = [
        (
            "Navn og Adresse",
            {
                "fields": (
                    "name",
                    "union_email",
                    "region",
                    "streetname",
                    "housenumber",
                    "floor",
                    "door",
                    "zipcode",
                    "city",
                    "placename",
                ),
                "description": "<p>Udfyld navnet på foreningen (f.eks København, \
            vestjylland) og adressen<p>",
            },
        ),
        (
            "Bestyrelsen",
            {
                "fields": (
                    "chairman",
                    "chairman_email",
                    "second_chair",
                    "second_chair_email",
                    "cashier",
                    "cashier_email",
                    "secretary",
                    "secratary_email",
                    "boardMembers",
                )
            },
        ),
        (
            "Info",
            {
                "fields": ("bank_main_org", "bank_account", "statues", "founded"),
                "description": "Indsæt et link til jeres vedtægter, hvornår I er stiftet (har holdt stiftende \
                generalforsamling) og jeres bankkonto hvis I har sådan en til foreningen.",
            },
        ),
    ]

    list_display = ("name",)


admin.site.register(Union, UnionAdmin)


class UnionDepartmentFilter(admin.SimpleListFilter):
    title = "Forening"
    parameter_name = "Union"

    def lookups(self, request, model_admin):
        unions = Union.objects.all()
        union_list = []
        for union in unions:
            union_list.append((str(union.pk), str(union)))
        return union_list

    def queryset(self, request, queryset):
        print(self.value())
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(union=self.value())


class DepartmentAdmin(admin.ModelAdmin):
    list_filter = (UnionDepartmentFilter,)
    raw_id_fields = ("union",)
    # Only show own departments

    def get_queryset(self, request):
        qs = super(DepartmentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(adminuserinformation__user=request.user)

    fieldsets = [
        (
            "Beskrivelse",
            {
                "fields": ("name", "union", "description", "open_hours"),
                "description": "<p>Lav en beskrivelse af jeres aktiviteter, teknologier og tekniske niveau.</p><p>Åbningstid er ugedag samt tidspunkt<p>",
            },
        ),
        ("Ansvarlig", {"fields": ("responsible_name", "responsible_contact")}),
        (
            "Adresse",
            {
                "fields": (
                    "streetname",
                    "housenumber",
                    "floor",
                    "door",
                    "zipcode",
                    "city",
                    "placename",
                )
            },
        ),
        (
            "Længde og Breddegrad",
            {
                "fields": ("longitude", "latitude"),
                "description": "<p>Hvis de ikke er sat opdateres de automatisk på et tidspunkt",
            },
        ),
        (
            "Afdelingssiden",
            {
                "fields": ("website", "isOpening", "isVisible"),
                "description": "<p>Har kan du vælge om afdeling skal vises på codingpirates.dk/afdelinger og om der skal være et link til en underside</p>",
            },
        ),
        (
            "Yderlige data",
            {
                "fields": ("has_waiting_list", "created", "closed_dtm"),
                "description": "<p>Venteliste betyder at børn har mulighed for at skrive sig på ventelisten (tilkendegive interesse for denne afdeling). Den skal typisk altid være krydset af.</p>",
                "classes": ("collapse",),
            },
        ),
    ]

    list_display = ("name",)


admin.site.register(Department, DepartmentAdmin)


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

    # inlines = [ActivityParticipantInline, ActivityInviteInline]


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
            ("none", "Ikke betalt"),
            ("ok", "Betalt"),
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


class VolunteerListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "frivillig i"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "volunteer"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            department_queryset = Department.objects.filter().order_by("zipcode")
        else:
            department_queryset = Department.objects.filter(
                adminuserinformation__user=request.user
            ).order_by("zipcode")

        departments = [("any", "Alle frivillige samlet"), ("none", "Ikke frivillig")]
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
            return (
                queryset.filter(volunteer__isnull=False)
                .filter(volunteer__removed__isnull=True)
                .distinct()
            )
        elif self.value() == "none":
            return (
                queryset.filter(volunteer__isnull=True).distinct()
                | queryset.exclude(volunteer__removed__isnull=True).distinct()
            )
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(
                volunteer__department__pk=self.value(), volunteer__removed__isnull=True
            )


class PersonParticipantListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Deltager på"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "participant_list"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            my_departments = Department.objects.filter()
        else:
            my_departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )

        activitys = [("none", "Deltager ikke"), ("any", "Alle deltagere samlet")]
        for activity in (
            Activity.objects.filter(department__in=my_departments)
            .order_by("start_date")
            .order_by("zipcode")
        ):
            activitys.append((str(activity.pk), str(activity)))

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
            return queryset.filter(member__activityparticipant__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(member__activityparticipant__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(member__activityparticipant__activity=self.value())


class PersonInvitedListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Inviteret til"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity_invited_list"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            my_departments = Department.objects.filter()
        else:
            my_departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )

        activitys = [("none", "Ikke inviteret til noget"), ("any", "Alle inviterede")]
        for activity in (
            Activity.objects.filter(department__in=my_departments)
            .order_by("start_date")
            .order_by("zipcode")
        ):
            activitys.append((str(activity.pk), str(activity)))

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
            return queryset.filter(activityinvite__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(activityinvite__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(activityinvite__activity=self.value())


class WaitingListInline(admin.TabularInline):
    model = WaitingList
    fields = ["on_waiting_list_since", "department", "number_on_waiting_list"]
    readonly_fields = fields
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "membertype",
        "family_url",
        "age_years",
        "zipcode",
        "added",
        "notes",
    )
    list_filter = (
        "membertype",
        "gender",
        VolunteerListFilter,
        PersonWaitinglistListFilter,
        PersonInvitedListFilter,
        PersonParticipantListFilter,
    )
    search_fields = ("name", "family__email", "notes")
    actions = ["invite_many_to_activity_action", "export_emaillist", "export_csv"]
    raw_id_fields = ("family", "user")

    inlines = [
        PaymentInline,
        VolunteerInline,
        ActivityInviteInline,
        MemberInline,
        WaitingListInline,
    ]

    def family_url(self, item):
        return format_html(
            '<a href="../family/%d">%s</a>' % (item.family.id, item.family.email)
        )

    family_url.allow_tags = True
    family_url.short_description = "Familie"
    list_per_page = 20

    def invite_many_to_activity_action(self, request, queryset):
        # Get list of available departments
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_persons"
        ):
            deparment_list_query = Department.objects.all()
        else:
            deparment_list_query = Department.objects.filter(
                adminuserinformation__user=request.user
            )
        deparment_list = [("-", "-")]
        for department in deparment_list_query:
            deparment_list.append((department.id, department.name))

        # Get list of active and future activities
        department_ids = deparment_list_query.values_list("id", flat=True)
        activity_list_query = Activity.objects.filter(end_date__gt=timezone.now())
        if not request.user.is_superuser:
            activity_list_query = activity_list_query.filter(
                department__in=department_ids
            )
        activity_list = [("-", "-")]
        for activity in activity_list_query:
            activity_list.append(
                (activity.id, activity.department.name + ", " + activity.name)
            )

        # Form used to select department and activity - redundant department is for double check
        class MassInvitationForm(forms.Form):
            department = forms.ChoiceField(label="Afdeling", choices=deparment_list)
            activity = forms.ChoiceField(label="Aktivitet", choices=activity_list)
            expire = forms.DateField(
                label="Udløber",
                widget=AdminDateWidget(),
                initial=timezone.now() + timedelta(days=30 * 3),
            )

        # Lookup all the selected persons - to show confirmation list
        persons = queryset

        context = admin.site.each_context(request)
        context["persons"] = persons
        context["queryset"] = queryset

        if request.method == "POST" and "department" in request.POST:
            # Post request with data
            mass_invitation_form = MassInvitationForm(request.POST)
            context["mass_invitation_form"] = mass_invitation_form

            if (
                mass_invitation_form.is_valid()
                and mass_invitation_form.cleaned_data["activity"] != "-"
                and mass_invitation_form.cleaned_data["department"] != "-"
            ):
                activity = Activity.objects.get(
                    pk=mass_invitation_form.cleaned_data["activity"]
                )

                # validate activity belongs to user and matches selected department
                if (
                    int(mass_invitation_form.cleaned_data["department"])
                    in department_ids
                ):
                    if activity.department.id == int(
                        mass_invitation_form.cleaned_data["department"]
                    ):
                        invited_counter = 0

                        # get list of already created invitations on selected persons
                        already_invited = Person.objects.filter(
                            activityinvite__activity=mass_invitation_form.cleaned_data[
                                "activity"
                            ],
                            activityinvite__person__in=queryset,
                        ).all()
                        list(already_invited)  # force lookup
                        already_invited_ids = already_invited.values_list(
                            "id", flat=True
                        )

                        # only save if all succeeds
                        try:
                            with transaction.atomic():
                                for current_person in queryset:
                                    if (
                                        current_person.id not in already_invited_ids
                                        and (
                                            activity.max_age
                                            >= current_person.age_years()
                                            >= activity.min_age
                                        )
                                    ):
                                        invited_counter = invited_counter + 1
                                        invitation = ActivityInvite(
                                            activity=activity,
                                            person=current_person,
                                            expire_dtm=mass_invitation_form.cleaned_data[
                                                "expire"
                                            ],
                                        )
                                        invitation.save()
                        except Exception:
                            messages.error(
                                request,
                                "Fejl - ingen personer blev inviteret! Der var problemer med "
                                + invitation.person.name
                                + ". Vær sikker på personen ikke allerede er inviteret og opfylder alderskravet.",
                            )
                            return

                        # return ok message
                        already_invited_text = ""
                        if already_invited.count():
                            already_invited_text = (
                                ". Dog var : "
                                + str.join(
                                    ", ", already_invited.values_list("name", flat=True)
                                )
                                + " allerede inviteret!"
                            )
                        messages.success(
                            request,
                            str(invited_counter)
                            + " af "
                            + str(queryset.count())
                            + " valgte personer blev inviteret til "
                            + str(activity)
                            + already_invited_text,
                        )
                        return

                    else:
                        messages.error(
                            request,
                            "Valgt aktivitet stemmer ikke overens med valgt afdeling",
                        )
                        return
                else:
                    messages.error(request, "Du kan kun invitere til egne afdelinger")
                    return
        else:
            context["mass_invitation_form"] = MassInvitationForm()

        return render(request, "admin/invite_many_to_activity.html", context)

    invite_many_to_activity_action.short_description = (
        "Inviter alle valgte til en aktivitet"
    )

    # needs 'view_full_address' to set personal details.
    # email and phonenumber only shown on adults.
    def get_fieldsets(self, request, person=None):
        if request.user.has_perm("members.view_full_address"):
            contact_fields = (
                "name",
                "streetname",
                "housenumber",
                "floor",
                "door",
                "city",
                "zipcode",
                "placename",
                "email",
                "phone",
                "family",
            )
        else:
            if person.membertype == Person.CHILD:
                contact_fields = ("name", "city", "zipcode", "family")
            else:
                contact_fields = ("name", "city", "zipcode", "email", "phone", "family")

        fieldsets = (
            ("Kontakt Oplysninger", {"fields": contact_fields}),
            ("Noter", {"fields": ("notes",)}),
            (
                "Yderlige informationer",
                {
                    "classes": ("collapse",),
                    "fields": (
                        "membertype",
                        "birthday",
                        "has_certificate",
                        "added",
                        "user",
                    ),
                },
            ),
        )

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        if type(obj) == Person and not request.user.is_superuser:
            return [
                "name",
                "streetname",
                "housenumber",
                "floor",
                "door",
                "city",
                "zipcode",
                "placename",
                "email",
                "phone",
                "family",
                "membertype",
                "birthday",
                "has_certificate",
                "added",
            ]
        else:
            return []

    def unique(self, item):
        return item.family.unique if item.family is not None else ""

    def export_emaillist(self, request, queryset):
        result_string = "kopier denne liste direkte ind i dit email program (Husk at bruge Bcc!)\n\n"
        family_email = []
        for person in queryset:
            if not person.family.dont_send_mails:
                family_email.append(person.family.email)
        result_string = result_string + ";\n".join(list(set(family_email)))
        result_string = (
            result_string
            + "\n\n\nHusk nu at bruge Bcc! ... IKKE TO: og heller IKKE CC: felterne\n\n"
        )

        return HttpResponse(result_string, content_type="text/plain")

    export_emaillist.short_description = "Exporter e-mail liste"

    def export_csv(self, request, queryset):
        result_string = '"Navn";"Alder";"Opskrevet";"Tlf (barn)";"Email (barn)";"Tlf (forælder)";"Email (familie)";"Postnummer"\n'
        for person in queryset:
            parent = person.family.get_first_parent()
            if parent:
                parent_phone = parent.phone
            else:
                parent_phone = ""

            if not person.family.dont_send_mails:
                person_email = person.email
                family_email = person.family.email
            else:
                person_email = ""
                family_email = ""

            result_string = (
                result_string
                + person.name
                + ";"
                + str(person.age_years())
                + ";"
                + str(person.added)
                + ";"
                + person.phone
                + ";"
                + person_email
                + ";"
                + parent_phone
                + ";"
                + family_email
                + ";"
                + person.zipcode
                + "\n"
            )
            response = HttpResponse(result_string, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="personer.csv"'
        return response

    export_csv.short_description = "Exporter CSV"

    # Only view persons related to users department (all family, via participant, waitinglist & invites)
    def get_queryset(self, request):
        qs = super(PersonAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_persons"
        ):
            return qs
        else:
            departments = Department.objects.filter(
                adminuserinformation__user=request.user
            ).values("id")
            return qs.filter(
                Q(
                    family__person__member__activityparticipant__activity__department__in=departments
                )
                | Q(family__person__waitinglist__department__in=departments)
                | Q(
                    family__person__activityinvite__activity__department__in=departments
                )
            ).distinct()


admin.site.register(Person, PersonAdmin)

admin.site.register(EmailTemplate)


# Define AdmingUserInformation as inline
class AdminUserInformationInline(admin.StackedInline):
    model = AdminUserInformation
    filter_horizontal = ("departments",)
    can_delete = False


# Define PersonInline
class PersonInline(admin.StackedInline):
    model = Person
    fields = ("name",)
    readonly_fields = ("name",)


# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (AdminUserInformationInline, PersonInline)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


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
