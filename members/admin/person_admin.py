import codecs
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse

from members.models import (
    Activity,
    AdminUserInformation,
    Department,
    Person,
    Volunteer,
)

from .filters.person_admin_filters import (
    PersonInvitedListFilter,
    PersonParticipantActiveListFilter,
    PersonParticipantCurrentYearListFilter,
    PersonParticipantLastYearListFilter,
    PersonParticipantListFilter,
    PersonWaitinglistListFilter,
    VolunteerListFilter,
    MunicipalityFilter,
    RegionFilter,
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
from members.utils.volunteer_confirmation import send_volunteer_user_confirmation_email


class PersonAdmin(admin.ModelAdmin):
    list_per_page = settings.LIST_PER_PAGE

    list_display = (
        "name",
        "membertype",
        "gender_text",
        "family_url",
        "age_years",
        "zipcode",
        "added_at",
        "family_referer",
        "notes",
    )
    list_filter = (
        "membertype",
        "gender",
        VolunteerListFilter,
        MunicipalityFilter,
        RegionFilter,
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
        "create_volunteer_action",
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

    def family_referer(self, item):
        return item.family.referer

    family_referer.allow_tags = True
    family_referer.short_description = "Hvor hørte de om os?"

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
                contact_fields = (
                    "name",
                    "city",
                    "zipcode",
                    "email",
                    "phone",
                    "family",
                )
        if request.user.has_perm("members.view_consent_information") or request:
            consent_fields = (
                "Samtykke",
                {
                    "classes": ("collapse",),
                    "fields": (
                        "allow_contact_from_cpdk",
                        "allow_contact_from_other",
                        "consent_preview_link",
                        "consent_by",
                        "consent_at",
                    ),
                },
            )
        else:
            consent_fields = ()

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

        if consent_fields:
            fieldsets += (consent_fields,)

        return fieldsets

    def consent_preview_link(self, obj):
        if obj.consent:
            full_url = reverse("consent_preview", args=[obj.consent.id])
            return format_html(
                f'<a href="{full_url}" target="_blank">Privatlivspolitik, ID: {obj.consent.id}</a>',
            )
        return "No consent available"

    consent_preview_link.short_description = "Privatlivspolitik"

    def get_readonly_fields(self, request, obj=None):
        if type(obj) is Person and not request.user.is_superuser:
            readonly_fields = [
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
            readonly_fields = []
        # Add consent fields to readonly
        readonly_fields += [
            "allow_contact_from_cpdk",
            "allow_contact_from_other",
            "consent",
            "consent_by",
            "consent_at",
            "consent_preview_link",
        ]
        return readonly_fields

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

    def create_volunteer_action(self, request, queryset):
        accessible_departments = AdminUserInformation.get_departments_admin(
            request.user
        ).order_by("name")

        class CreateVolunteerForm(forms.Form):
            department = forms.ModelChoiceField(
                queryset=accessible_departments,
                label="Afdeling",
            )
            activity = forms.ModelChoiceField(
                queryset=Activity.objects.none(),
                label="Aktivitet",
                required=False,
                empty_label="--- Ingen aktivitet ---",
            )
            start_date = forms.DateField(
                label="Startdato",
                widget=AdminDateWidget(),
                initial=timezone.now().date,
            )
            end_date = forms.DateField(
                label="Slutdato",
                widget=AdminDateWidget(),
                required=False,
            )

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields["activity"].label_from_instance = (
                    lambda obj: "[{} - {}] {}".format(
                        obj.start_date.strftime("%Y-%m-%d") if obj.start_date else "-",
                        obj.end_date.strftime("%Y-%m-%d") if obj.end_date else "-",
                        obj.name,
                    )
                )
                department_id = None

                if self.is_bound:
                    department_id = self.data.get("department")
                else:
                    department_id = self.initial.get("department")

                if department_id:
                    try:
                        department_id = int(department_id)
                        self.fields["activity"].queryset = Activity.objects.filter(
                            department_id=department_id,
                            activitytype__id__in=["FORLØB", "ARRANGEMENT"],
                        ).order_by("-start_date", "name")
                    except (TypeError, ValueError):
                        self.fields["activity"].queryset = Activity.objects.none()

            def clean(self):
                cleaned_data = super().clean()
                department = cleaned_data.get("department")
                activity = cleaned_data.get("activity")
                start_date = cleaned_data.get("start_date")
                end_date = cleaned_data.get("end_date")

                if activity and department and activity.department_id != department.id:
                    self.add_error(
                        "activity",
                        "Aktiviteten skal tilhøre den valgte afdeling.",
                    )

                if start_date and end_date and end_date < start_date:
                    self.add_error(
                        "end_date",
                        "Slutdato må ikke være før startdato.",
                    )

                return cleaned_data

        if queryset.count() != 1:
            self.message_user(
                request,
                "Du må kun vælge én person ad gangen for at oprette en frivillig.",
                level="error",
            )
            return HttpResponseRedirect(request.get_full_path())

        person = queryset.first()

        context = admin.site.each_context(request)
        context["person"] = person
        context["queryset"] = queryset
        context["action_name"] = "create_volunteer_action"

        if request.method == "POST" and "department" in request.POST:
            create_volunteer_form = CreateVolunteerForm(request.POST)
            context["create_volunteer_form"] = create_volunteer_form

            if request.POST.get("refresh_activity_choices") == "1":
                return render(
                    request,
                    "admin/create_volunteer.html",
                    context,
                )

            if create_volunteer_form.is_valid():
                department = create_volunteer_form.cleaned_data["department"]
                activity = create_volunteer_form.cleaned_data["activity"]

                if Volunteer.objects.filter(
                    person=person,
                    department=department,
                    activity=activity,
                    removed__isnull=True,
                ).exists():
                    create_volunteer_form.add_error(
                        None,
                        "Personen er allerede registreret som aktiv frivillig med denne kombination af afdeling og aktivitet.",
                    )
                    return render(
                        request,
                        "admin/create_volunteer.html",
                        context,
                    )

                volunteer = Volunteer.objects.create(
                    person=person,
                    department=department,
                    activity=activity,
                    start_date=create_volunteer_form.cleaned_data["start_date"],
                    end_date=create_volunteer_form.cleaned_data["end_date"],
                    user_confirmation_status=Volunteer.UserConfirmationStatus.WAITING_FOR_USER,
                )

                send_volunteer_user_confirmation_email(volunteer)

                self.message_user(
                    request,
                    f"{person.name} er oprettet som frivillig og afventer brugerens godkendelse.",
                )
                return HttpResponseRedirect(request.get_full_path())
        else:
            context["create_volunteer_form"] = CreateVolunteerForm()

        return render(
            request,
            "admin/create_volunteer.html",
            context,
        )

    create_volunteer_action.short_description = "Opret frivillig"
    create_volunteer_action.allowed_permissions = ("view",)

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
                    try:
                        person.anonymize(request)
                    except Exception as e:
                        self.message_user(
                            request,
                            f"Fejl under anonymisering: {str(e)}",
                            level="error",
                        )
                        return HttpResponseRedirect(request.get_full_path())

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
