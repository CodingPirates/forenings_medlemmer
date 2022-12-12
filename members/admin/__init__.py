from uuid import uuid4
from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from django.db.models.functions import Lower
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms import Textarea
from copy import deepcopy

from members.models import (
    Address,
    AdminUserInformation,
    Person,
    Department,
    Union,
    Volunteer,
    Member,
    Activity,
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
    fields = ("admin_link", "membertype", "zipcode", "added_at", "notes", "email")
    readonly_fields = fields
    can_delete = False
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    fields = ("added_at", "payment_type", "confirmed_at", "rejected_at", "amount_ore")
    readonly_fields = ("family",)
    extra = 0


class VolunteerInline(admin.TabularInline):
    model = Volunteer
    fields = ("department", "added_at", "confirmed", "removed")
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


class ActivityParticipantListCurrentYearFilter(admin.SimpleListFilter):
    # Title shown in filter view. \u2265 : ≥ (større end eller lig med)
    title = "Efter aktivitet (\u2265 år " + str(timezone.now().year) + ")"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    # def choices(self, changelist):
    #    choices = list(super().choices(changelist))
    #    choices[0]['display'] = f'Alle akvititeter i {str(timezone.now().year)}'
    #    return choices

    def lookups(self, request, model_admin):
        activitys = [
            #    ("none", "Intet filter"),
        ]
        for act in Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user),
            start_date__year__gte=timezone.now().year,
        ).order_by("department__name", "-start_date"):
            activitys.append((str(act.pk), str(act)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            # return queryset.filter(activity__start_date__year=timezone.now().year)
            return queryset
        # if self.value() == "none":
        #    return queryset.exclude(activity__isnull = True)
        else:
            return queryset.filter(activity=self.value())


class ActivityParticipantListLastYearFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Efter aktivitet (= år " + str(timezone.now().year - 1) + ")"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    # def choices(self, changelist):
    #    choices = list(super().choices(changelist))
    #        choices[0]['display'] = f'Alle akvititeter i {str(timezone.now().year)}'
    #    choices[0]['display'] = 'Intet filter'
    #    return choices

    def lookups(self, request, model_admin):
        activitys = [
            # ("all", f'Alle aktiviteter i {str(timezone.now().year - 1)}')
        ]
        for act in Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user),
            start_date__year=timezone.now().year - 1,
        ).order_by("department__name", "-start_date"):
            activitys.append((str(act.pk), str(act)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
            # return queryset.exclude(activity__isnull = True)
        # elif self.value() == "all":
        #    return queryset
        # return queryset.filter(activity__start_date__year=timezone.now().year-1)
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
    date_hierarchy = "activity__start_date"

    list_filter = (
        ActivityParticipantUnionFilter,
        ActivityParticipantDepartmentFilter,
        ActivityParticipantListCurrentYearFilter,
        ActivityParticipantListLastYearFilter,
        ActivityParticipantListOldYearsFilter,
        ParticipantPaymentListFilter,
    )
    # list_display_links = ("member",)
    # raw_id_fields = ("activity", "member")
    # search_fields = ("member__person__name",)
    # Member.short_description = "Navn"
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
        #        "export_csv_simple1",
        #        "export_csv_simple2",
        #        "export_csv_full1",
        "export_csv_full2",
    ]

    def person_age_years(self, item):
        return item.member.person.age_years()

    person_age_years.short_description = "Alder"
    person_age_years.admin_order_field = "-member__person__birthday"

    def person_gender(self, item):
        if item.member.person.gender == "MA":
            return "Dreng"
        elif item.member.person.gender == "FE":
            return "Pige"
        else:
            return "Andet"

    person_gender.short_description = "Køn"

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
            return "andet"

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

    def export_csv_full2(self, request, queryset):
        result_string = '"Forening"; "Afdeling"; "Aktivitet"; "Navn"; "Alder; "Køn"; "Post-nr"; "Betalingsinfo"; "forældre navn"; "forældre email"; "forældre tlf"; "Note til arrangørerne"\n'
        today = timezone.now().date()
        for p in queryset:
            if p.member.person.gender == "MA":
                gender = "Dreng"
            elif p.member.person.gender == "FM":
                gender = "Pige"
            else:
                gender = p.member.person.gender
            birthday = p.member.person.birthday
            age = (
                today.year
                - birthday.year
                - ((today.month, today.day) < (birthday.month, birthday.day))
            )

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
                + str(age)
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
                + self.note
                + "\n"
            )
        response = HttpResponse(result_string, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="deltagere.csv"'
        return response

    export_csv_full2.short_description = "CSV Export (Forening; Afdeling; Aktivitet; Navn; Alder; Køn; Post-nr; Betalingsinfo; forældre-navn; forældre-email; forældre-telefon; Note-til-arrangørerne)"


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
        "rejected_at",
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
                    "rejected_at",
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


admin.site.register(Equipment, EquipmentAdmin)

User = get_user_model()
admin.site.unregister(User)


class AdminUserInformationInline(admin.StackedInline):
    model = AdminUserInformation
    filter_horizontal = ("departments", "unions")
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = [AdminUserInformationInline, PersonInline]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        if not obj:
            return fieldsets

        if not request.user.is_superuser:  # or request.user.pk == obj.pk:  #
            fieldsets = deepcopy(fieldsets)
            for fieldset in fieldsets:
                if "is_superuser" in fieldset[1]["fields"]:
                    if type(fieldset[1]["fields"] == tuple):
                        fieldset[1]["fields"] = list(fieldset[1]["fields"])
                        fieldset[1]["fields"].remove("is_superuser")
                        # break
                if "user_permissions" in fieldset[1]["fields"]:
                    if type(fieldset[1]["fields"] == tuple):
                        fieldset[1]["fields"] = list(fieldset[1]["fields"])
                        fieldset[1]["fields"].remove("user_permissions")
                        # break
                if "username" in fieldset[1]["fields"]:
                    if type(fieldset[1]["fields"] == tuple):
                        fieldset[1]["fields"] = list(fieldset[1]["fields"])
                        fieldset[1]["fields"].remove("username")
                        # break
        return fieldsets


admin.site.register(User, CustomUserAdmin)
