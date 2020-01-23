from datetime import timedelta

from django import forms
from django.contrib import admin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.shortcuts import render
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib import messages

from members.models import (
    Activity,
    ActivityInvite,
    Department,
    Person,
)

from .person_admin_filters import (
    VolunteerListFilter,
    PersonWaitinglistListFilter,
    PersonInvitedListFilter,
    PersonParticipantListFilter,
)

from .inlines import (
    MemberInline,
    PaymentInline,
    VolunteerInline,
    ActivityInviteInline,
    WaitingListInline,
)


class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "membertype",
        "gender",
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
