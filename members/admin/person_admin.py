import codecs
from django import forms
from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.html import format_html

from members.models import (
    Department,
    Person,
)

from .person_admin_filters import (
    PersonInvitedListFilter,
    PersonParticipantActiveListFilter,
    PersonParticipantCurrentYearListFilter,
    PersonParticipantLastYearListFilter,
    PersonParticipantListFilter,
    PersonWaitinglistListFilter,
    VolunteerListFilter,
    MunicipalityFilter,
    AnonymizedFilter,
)

from .inlines import (
    ActivityInviteInline,
    PaymentInline,
    VolunteerInline,
    WaitingListInline,
    EmailItemInline,
)

from members.admin.admin_actions import AdminActions


class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "membertype",
        "gender_text",
        "family_url",
        "age_years",
        "zipcode",
        "added_at",
        "notes",
    )
    list_filter = (
        "membertype",
        "gender",
        VolunteerListFilter,
        MunicipalityFilter,
        PersonWaitinglistListFilter,
        PersonInvitedListFilter,
        PersonParticipantListFilter,
        PersonParticipantActiveListFilter,
        PersonParticipantCurrentYearListFilter,
        PersonParticipantLastYearListFilter,
        AnonymizedFilter,
    )
    search_fields = ("name", "family__email", "notes")
    autocomplete_fields = ["municipality"]
    actions = [
        AdminActions.invite_many_to_activity_action,
        "export_emaillist",
        "export_csv",
    ]
    raw_id_fields = ("family", "user")

    inlines = [
        PaymentInline,
        VolunteerInline,
        ActivityInviteInline,
        WaitingListInline,
        EmailItemInline,
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)

        if request.user.has_perm("members.anonymize_persons"):
            actions["anonymize_persons"] = (
                lambda modeladmin, request, queryset: self.anonymize_persons(
                    request, queryset
                ),
                "anonymize_persons",
                self.anonymize_persons.short_description,
            )

        return actions

    def family_url(self, item):
        return format_html(
            '<a href="../family/%d">%s</a>' % (item.family.id, item.family.email)
        )

    family_url.allow_tags = True
    family_url.short_description = "Familie"
    list_per_page = 20

    def gender_text(self, item):
        return item.gender_text()

    gender_text.short_description = "Køn"

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
                "municipality",
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
                        "added_at",
                        "user",
                        "gender",
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
                "municipality",
                "email",
                "phone",
                "family",
                "membertype",
                "birthday",
                "has_certificate",
                "added_at",
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
        result_string = "Navn;Alder;Køn;Opskrevet;Tlf (barn);Email (barn);"
        result_string += "Tlf (forælder);Email (familie);Postnummer;Noter\n"
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
                + str(person.gender_text())
                + ";"
                + str(person.added_at.strftime("%Y-%m-%d %H:%M"))
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
                + ";"
                + '"'
                + person.notes.replace('"', '""')
                + '"'
                + "\n"
            )
            response = HttpResponse(
                f'{codecs.BOM_UTF8.decode("utf-8")}{result_string}',
                content_type="text/csv; charset=utf-8",
            )
            response["Content-Disposition"] = 'attachment; filename="personer.csv"'
        return response

    export_csv.short_description = "CSV Export"

    def anonymize_persons(self, request, queryset):
        class MassConfirmForm(forms.Form):
            confirmation = forms.BooleanField(
                label="Jeg godkender at ovenstående person anonymiseres",
                required=True,
                widget=forms.CheckboxInput(
                    attrs={"style": "color: blue; width: unset;"}
                ),
            )

        if not request.user.has_perm("members.anonymize_persons"):
            self.message_user(
                request, "Du har ikke tilladelse til at anonymisere personer."
            )
            return HttpResponseRedirect(request.get_full_path())

        if queryset.count() > 1:
            self.message_user(
                request, "Kun én person kan anonymiseres ad gangen.", level="error"
            )
            return HttpResponseRedirect(request.get_full_path())

        for person in queryset:
            if person.anonymized:
                self.message_user(
                    request,
                    "Den valgte person er allerede anonymiseret.",
                    level="error",
                )
                return HttpResponseRedirect(request.get_full_path())

        persons = queryset

        context = admin.site.each_context(request)
        context["persons"] = persons
        context["queryset"] = queryset

        if request.method == "POST" and "confirmation" in request.POST:
            form = MassConfirmForm(request.POST)

            if form.is_valid():
                context["mass_confirmation_form"] = form
                for person in queryset:
                    person.anonymize(request)

                self.message_user(request, "Personen er blevet anonymiseret.")
                return HttpResponseRedirect(request.get_full_path())

        context["mass_confirmation_form"] = MassConfirmForm()

        return render(
            request,
            "admin/anonymize_persons.html",
            context,
        )

    anonymize_persons.short_description = "Anonymisér person"

    # Only view persons related to users department (all family, via participant, waitinglist & invites)
    def get_queryset(self, request):
        qs = super(PersonAdmin, self).get_queryset(request)
        if (
            request.user.is_superuser
            or request.user.has_perm("members.view_all_persons")
            or request.user.has_perm("members.view_all_departments")
        ):
            return qs
        else:
            departments = Department.objects.filter(
                adminuserinformation__user=request.user
            ).values("id")
            return qs.filter(
                Q(
                    family__person__activityparticipant__activity__department__in=departments
                )
                | Q(family__person__waitinglist__department__in=departments)
                | Q(
                    family__person__activityinvite__activity__department__in=departments
                )
            ).distinct()
