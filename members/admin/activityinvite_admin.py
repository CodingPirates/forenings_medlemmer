import codecs
from datetime import timedelta
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.widgets import AdminDateWidget
from django.db import transaction
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.db.models import Exists, OuterRef

from members.models import (
    Activity,
    ActivityInvite,
    ActivityParticipant,
    AdminUserInformation,
    Department,
    Person,
)

from members.admin.admin_actions import AdminActions


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

    actions = [
        "export_csv_invitation_info",
        "extend_invitations",
        AdminActions.invite_many_to_activity_action,
    ]

    form = ActivityInviteAdminForm

    # Only show invitation to own activities
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        qs = queryset.annotate(
            is_participating=Exists(
                ActivityParticipant.objects.filter(
                    person=OuterRef("person"), activity=OuterRef("activity")
                )
            )
        )

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
    person_age_years.admin_order_field = "person__birthday"

    def person_zipcode(self, item):
        return item.person.zipcode

    person_zipcode.short_description = "Postnummer"
    person_zipcode.admin_order_field = "person__zipcode"

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
        return item.is_participating

    participating.short_description = "Deltager"
    participating.boolean = True
    participating.admin_order_field = "is_participating"

    def export_csv_invitation_info(self, request, queryset):
        def handle_quote(str, sep):
            return '"' + str.replace('"', '""') + '"' + sep

        result_string = (
            '"Forening"; "Afdeling"; "Aktivitet"; "Deltager"; '
            '"Deltager-email"; "Familie-email"; "Pris"; "Pris note"; '
            '"Ekstra email info" ;"Deltager i aktiviteten"; '
            '"Invitationsdato"; "Udløbsdato"; "Afslåetdato"\n'
        )

        for invitation in queryset:
            participate = (
                "Ja"
                if invitation.person.activityparticipant_set.filter(
                    activity=invitation.activity
                ).exists()
                else "Nej"
            )
            expire_date = (
                ""
                if invitation.expire_dtm is None
                else invitation.expire_dtm.strftime("%Y-%m-%d")
            )
            rejected_date = (
                ""
                if invitation.rejected_at is None
                else invitation.rejected_at.strftime("%Y-%m-%d")
            )

            result_string += (
                handle_quote(invitation.activity.department.union.name, ";")
                + handle_quote(invitation.activity.department.name, ";")
                + handle_quote(invitation.activity.name, ";")
                + handle_quote(invitation.person.name, ";")
                + handle_quote(invitation.person.email, ";")
                + handle_quote(invitation.person.family.email, ";")
                + handle_quote(str(invitation.price_in_dkk), ";")
                + handle_quote(invitation.price_note, ";")
                + handle_quote(invitation.extra_email_info, ";")
                + handle_quote(participate, ";")
                + handle_quote(invitation.invite_dtm.strftime("%Y-%m-%d"), ";")
                + handle_quote(expire_date, ";")
                + handle_quote(rejected_date, "\n")
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

    def extend_invitations(modelAdmin, request, queryset):
        class ExtendInvitationsForm(forms.Form):
            expires = forms.DateField(
                label="Udløber",
                widget=AdminDateWidget(),
                initial=timezone.now() + timedelta(days=14),
            )

        invitations = queryset

        context = admin.site.each_context(request)
        context["invitations"] = invitations
        context["queryset"] = queryset

        expires = timezone.now() + timedelta(days=14)
        context["expires"] = expires

        if request.method == "POST" and "expires" in request.POST:
            extend_invitations_form = ExtendInvitationsForm(request.POST)
            context["extend_invitations_form"] = extend_invitations_form

            if extend_invitations_form.is_valid():
                expires = extend_invitations_form.cleaned_data["expires"]

                if expires < timezone.now().date():
                    messages.error(
                        request,
                        "Fejl - den angivne udløbsdato er før dags dato.",
                    )
                    return

                updated_invitations = 0
                skipped_invitations = 0
                try:
                    with transaction.atomic():
                        for invitation in invitations:
                            if invitation.expire_dtm > expires:
                                skipped_invitations += 1
                                continue

                            invitation.expire_dtm = expires
                            invitation.save()
                            updated_invitations += 1
                except Exception as E:
                    messages.error(
                        request,
                        f"Fejl - ingen invitationer blev forlænget! Følgende fejl opstod: {E=}",
                    )
                    return

                status_text = f"{updated_invitations} invitationer blev forlænget til {formats.date_format(expires, 'DATE_FORMAT')}."
                if skipped_invitations > 0:
                    status_text += f"<br/>{skipped_invitations} invitationer blev sprunget over, da de allerede havde en senere udløbsdato."
                messages.success(
                    request,
                    mark_safe(status_text),
                )

                return
        else:
            context["extend_invitations_form"] = ExtendInvitationsForm()

        return render(request, "admin/extend_invitations.html", context)

    extend_invitations.short_description = "Forlæng invitationer"
