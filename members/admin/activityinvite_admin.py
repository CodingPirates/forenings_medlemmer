import codecs
from django import forms
from django.contrib import admin
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.html import escape

from members.models import (
    Activity,
    ActivityInvite,
    AdminUserInformation,
    Department,
    Person,
)


class ActivityInviteAdminForm(forms.ModelForm):
    class Meta:
        model = ActivityInvite
        exclude = []

    def __init__(self, *args, **kwds):
        super(ActivityInviteAdminForm, self).__init__(*args, **kwds)
        self.fields["person"].queryset = Person.objects.order_by(Lower("name"))


class ActivityInviteUnionListFilter(admin.SimpleListFilter):
    title = "Lokalforeninger"
    parameter_name = "activity__department__union"

    def lookups(self, request, model_admin):
        unions = []
        for union in AdminUserInformation.get_unions_admin(request.user).order_by(
            "name"
        ):
            unions.append((str(union.pk), union.name))

        return unions

    def queryset(self, request, queryset):
        if self.value() == "any":
            return queryset.exclude(activity__department__union__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__department__union__pk=self.value())


class ActivityInviteDepartmentListFilter(admin.SimpleListFilter):
    title = "Afdelinger"
    parameter_name = "activity__department"

    def lookups(self, request, model_admin):
        departments = []
        for department in AdminUserInformation.get_departments_admin(
            request.user
        ).order_by("name"):
            departments.append((str(department.pk), department.name))
        return departments

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__department__pk=self.value())


class ActivityInviteListCurrentFilter(admin.SimpleListFilter):
    title = "Nuværende og kommende aktiviteter"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for act in (
            Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user),
                end_date__gte=timezone.now(),
            )
            .order_by("department__name", "-start_date")
            .distinct()
        ):
            activitys.append((str(act.pk), str(act)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity=self.value())


class ActivityInviteListFinishedFilter(admin.SimpleListFilter):
    title = "Tidligere aktiviteter"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for act in (
            Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user),
                end_date__lte=timezone.now(),
            )
            .order_by("department__name", "-start_date")
            .distinct()
        ):
            activitys.append((str(act.pk), str(act)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity=self.value())


class ActivityInviteAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = "Invitation"
        verbose_name_plural = "Invitationer"

    list_display = (
        "pk",
        "person_link",
        "activity_link",
        "person_age_years",
        "person_zipcode",
        "invite_dtm",
        "expire_dtm",
        "rejected_at",
        "price_in_dkk",
        "price_note",
        "extra_email_info",
        "participating",
        "activity_department_union_link",
        "activity_department_link",
    )
    list_filter = (
        ActivityInviteUnionListFilter,
        ActivityInviteDepartmentListFilter,
        ActivityInviteListCurrentFilter,
        ActivityInviteListFinishedFilter,
    )
    date_hierarchy = "activity__start_date"

    search_fields = (
        "activity__department__union__name",
        "activity__department__name",
        "activity__name",
        "person__name",
    )
    search_help_text = mark_safe(
        "Du kan søge på forening, afdeling, aktivitet eller person. <br>Vandret dato-filter er for aktivitetens startdato."
    )

    actions = ["export_csv_invitation_info"]

    form = ActivityInviteAdminForm

    # Only show invitation to own activities
    def get_queryset(self, request):
        qs = super(ActivityInviteAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
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

    def activity_department_union_link(self, item):
        url = reverse(
            "admin:members_union_change", args=[item.activity.department.union_id]
        )
        link = '<a href="%s">%s</a>' % (
            url,
            escape(item.activity.department.union.name),
        )
        return mark_safe(link)

    activity_department_union_link.short_description = "Forening"
    activity_department_union_link.admin_order_field = (
        "activity__department__union__name"
    )

    def activity_department_link(self, item):
        url = reverse(
            "admin:members_department_change", args=[item.activity.department_id]
        )
        link = '<a href="%s">%s</a>' % (url, escape(item.activity.department.name))
        return mark_safe(link)

    activity_department_link.short_description = "Afdeling"
    activity_department_link.admin_order_field = "activity__department__name"

    def activity_link(self, item):
        url = reverse("admin:members_activity_change", args=[item.activity.id])
        link = '<a href="%s">%s</a>' % (url, escape(item.activity.name))
        return mark_safe(link)

    activity_link.short_description = "Aktivitet"
    activity_link.admin_order_field = "activity__name"

    def person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.person_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.person.name))
        return mark_safe(link)

    person_link.short_description = "Person"
    person_link.admin_order_field = "person__name"

    def participating(self, item):
        return item.person.activityparticipant_set.filter(
            activity=item.activity
        ).exists()

    participating.short_description = "Deltager"
    participating.boolean = True

    def export_csv_invitation_info(self, request, queryset):
        result_string = """"Forening"; "Afdeling"; "Aktivitet"; "Deltager";\
            "Deltager-email"; "Familie-email"; "Pris"; "Pris note"; "Ekstra email info" ;\
            "Deltager i aktiviteten"; "Invitationsdato"; "Udløbsdato"; "Afslåetdato"\n"""

        for invitation in queryset:
            if invitation.person.activityparticipant_set.filter(
                activity=invitation.activity
            ).exists():
                participate = "Ja"
            else:
                participate = "Nej"
            if invitation.expire_dtm is None:
                expire_date = ""
            else:
                expire_date = invitation.expire_dtm.strftime("%Y-%m-%d")
            if invitation.rejected_at is None:
                rejected_date = ""
            else:
                rejected_date = invitation.rejected_at.strftime("%Y-%m-%d")

            result_string = (
                result_string
                + invitation.activity.department.union.name
                + ";"
                + invitation.activity.department.name
                + ";"
                + invitation.activity.name
                + ";"
                + invitation.person.name
                + ";"
                + invitation.person.email
                + ";"
                + invitation.person.family.email
                + ";"
                + str(invitation.price_in_dkk)
                + ";"
                + '"'
                + invitation.price_note.replace('"', '""')
                + '"'
                + ";"
                + '"'
                + invitation.extra_email_info.replace('"', '""')
                + '"'
                + ";"
                + participate
                + ";"
                + invitation.invite_dtm.strftime("%Y-%m-%d")
                + ";"
                + expire_date
                + ";"
                + rejected_date
                + "\n"
            )
        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("utf-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = (
            'attachment; filename="invitationsoversigt.csv"'
        )
        return response

    export_csv_invitation_info.short_description = "Exporter Invitationsinformationer"
