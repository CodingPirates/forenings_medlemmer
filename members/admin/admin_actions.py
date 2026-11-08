import codecs
from datetime import timedelta
from django import forms
from django.contrib import admin
from django.contrib import messages

from django.contrib.admin.widgets import AdminDateWidget
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect

from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.shortcuts import render
import members.models.emailtemplate
import members.models.waitinglist
from members.utils.age_check import check_is_person_too_young
from members.utils.age_check import check_is_person_too_old

from members.models import (
    Activity,
    ActivityInvite,
    ActivityParticipant,
    AdminUserInformation,
    Department,
    Person,
    Volunteer,
    WaitingList,
)
from members.utils.volunteer_confirmation import send_volunteer_user_confirmation_email


class AdminActions(admin.ModelAdmin):
    def invite_many_to_activity_action(modelAdmin, request, queryset):
        template = members.models.emailtemplate.EmailTemplate.objects.get(
            idname="ACT_INVITE"
        )

        # Get list of available departments
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
            department_list_query = Department.objects.filter(
                closed_dtm__isnull=True
            ).order_by("name")
        else:
            department_list_query = Department.objects.filter(
                adminuserinformation__user=request.user, closed_dtm__isnull=True
            ).order_by("name")
        department_list = [("-", "-")]
        for department in department_list_query:
            department_list.append((department.id, department.name))

        # Get list of active and future activities
        department_ids = department_list_query.values_list("id", flat=True)
        activity_list_query = Activity.objects.filter(
            end_date__gt=timezone.now()
        ).order_by("department__name", "name")
        if not request.user.is_superuser and not request.user.has_perm(
            "members.view_all_departments"
        ):
            activity_list_query = activity_list_query.filter(
                department__in=department_ids
            ).order_by("department__name", "name")
        activity_list = [("-", "-")]
        for activity in activity_list_query:
            activity_list.append(
                (activity.id, activity.department.name + ", " + activity.name)
            )

        # Form used to select department and activity - redundant department is for double check
        class MassInvitationForm(forms.Form):
            department = forms.ChoiceField(label="Afdeling", choices=department_list)
            activity = forms.ChoiceField(label="Aktivitet", choices=activity_list)
            expire = forms.DateField(
                label="Udløber",
                widget=AdminDateWidget(),
                initial=timezone.now() + timedelta(days=14),
            )
            email_text = forms.CharField(
                label="Email ekstra info", widget=forms.Textarea, required=False
            )
            special_price_in_dkk = forms.DecimalField(
                label="Særpris", max_digits=10, decimal_places=2, required=False
            )
            special_price_note = forms.CharField(
                label="Note om særpris", widget=forms.Textarea, required=False
            )

        # Lookup all the selected persons - to show confirmation list
        # Check if it's called from Waiting List
        if queryset.model is WaitingList:
            q = [wl.person.pk for wl in queryset]
            persons = Person.objects.filter(pk__in=q)
        # or if it's called from the Participants list
        elif queryset.model is ActivityParticipant:
            q = [pa.person.pk for pa in queryset]
            persons = Person.objects.filter(pk__in=q)
        elif queryset.model is ActivityInvite:
            persons = Person.objects.filter(
                pk__in=queryset.values_list("person_id", flat=True)
            )
        elif queryset.model is Volunteer:
            persons = Person.objects.filter(
                pk__in=queryset.values_list("person_id", flat=True)
            )
        else:
            persons = queryset

        context = admin.site.each_context(request)
        if persons is None:
            q = [wl.person.pk for wl in queryset]
            persons = Person.objects.filter(pk__in=q)
            # queryset = persons

        context["persons"] = persons
        context["queryset"] = queryset
        context["emailtemplate"] = template
        context["action_name"] = request.POST.get(
            "action", "invite_many_to_activity_action"
        )

        if request.method == "POST" and "activity" in request.POST:
            # Post request with data
            mass_invitation_form = MassInvitationForm(request.POST)
            context["mass_invitation_form"] = mass_invitation_form

            if (
                mass_invitation_form.is_valid()
                and mass_invitation_form.cleaned_data["activity"] != "-"
                and mass_invitation_form.cleaned_data["department"] != "-"
            ):
                #  Department and Activity selected
                activity = Activity.objects.get(
                    pk=mass_invitation_form.cleaned_data["activity"]
                )

                if mass_invitation_form.cleaned_data["special_price_in_dkk"] is None:
                    special_price_in_dkk = activity.price_in_dkk
                else:
                    special_price_in_dkk = mass_invitation_form.cleaned_data[
                        "special_price_in_dkk"
                    ]

                if (
                    special_price_in_dkk != activity.price_in_dkk
                    and mass_invitation_form.cleaned_data["special_price_note"] == ""
                ):
                    mass_invitation_form.add_error(
                        "special_price_note",
                        "Du skal angive en begrundelse for den særlige pris for denne deltager.",
                    )
                    context["mass_invitation_form"] = mass_invitation_form
                    return render(
                        request, "admin/invite_many_to_activity.html", context
                    )

                min_amount = activity.get_min_amount(activity.activitytype.id)

                if (
                    special_price_in_dkk is not None
                    and special_price_in_dkk < min_amount
                ):
                    messages.error(
                        request,
                        f"Prisen er for lav. Denne type aktivitet skal koste mindst {min_amount} kr.",
                    )
                    return

                # validate activity belongs to user and matches selected department
                if (
                    int(mass_invitation_form.cleaned_data["department"])
                    in department_ids
                ):
                    if activity.department.id == int(
                        mass_invitation_form.cleaned_data["department"]
                    ):
                        invited_counter = 0
                        persons_too_young = []
                        persons_too_old = []
                        persons_already_invited = []
                        persons_already_participant = []
                        persons_invited = []
                        persons_dont_send_mails = []

                        # get list of already created invitations on selected persons
                        already_invited = Person.objects.filter(
                            activityinvite__activity=mass_invitation_form.cleaned_data[
                                "activity"
                            ],
                            activityinvite__person__in=persons,
                        ).all()
                        list(already_invited)  # force lookup
                        already_invited_ids = already_invited.values_list(
                            "id", flat=True
                        )

                        # get list of current participants on selected persons
                        already_participant = Person.objects.filter(
                            activityparticipant__activity=mass_invitation_form.cleaned_data[
                                "activity"
                            ],
                            activityparticipant__person__in=persons,
                        ).all()
                        list(already_participant)  # force lookup
                        already_participant_ids = already_participant.values_list(
                            "id", flat=True
                        )

                        # only save if all succeeds
                        invitation = []
                        try:
                            with transaction.atomic():
                                # for current_person in queryset:
                                for current_person in persons:
                                    # TODO: refactor this (according to Kristoffer)
                                    # Check for the DontSendMails flag
                                    if current_person.family.dont_send_mails:
                                        persons_dont_send_mails.append(
                                            current_person.name
                                        )
                                    # check for already participant
                                    elif current_person.id in already_participant_ids:
                                        persons_already_participant.append(
                                            current_person.name
                                        )

                                    # Check for already invited
                                    elif current_person.id in already_invited_ids:
                                        persons_already_invited.append(
                                            current_person.name
                                        )

                                    # Check for age constraint: too young ?
                                    elif check_is_person_too_young(
                                        activity, current_person
                                    ):
                                        persons_too_young.append(current_person.name)
                                    # Check for age constraint: too old ?
                                    elif check_is_person_too_old(
                                        activity, current_person
                                    ):
                                        persons_too_old.append(current_person.name)
                                    # Otherwise - person can be invited
                                    else:
                                        invited_counter = invited_counter + 1
                                        invitation = ActivityInvite(
                                            activity=activity,
                                            person=current_person,
                                            expire_dtm=mass_invitation_form.cleaned_data[
                                                "expire"
                                            ],
                                            extra_email_info=mass_invitation_form.cleaned_data[
                                                "email_text"
                                            ],
                                            price_in_dkk=special_price_in_dkk,
                                            price_note=mass_invitation_form.cleaned_data[
                                                "special_price_note"
                                            ],
                                        )
                                        invitation.save()
                                        persons_invited.append(current_person.name)

                        except Exception as E:
                            messages.error(
                                request,
                                "Fejl - ingen personer blev inviteret! Der var problemer med "
                                + (invitation.person.name if invitation else "(n/a)")
                                + ". Vær sikker på personen ikke allerede er inviteret og opfylder alderskravet."
                                + f"{E=}",
                            )
                            return

                        # Message about new invites:
                        invited_text = (
                            "<u>"
                            + str(invited_counter)
                            + " af "
                            + str(persons.count())
                            + " valgte personer blev inviteret til "
                            + escape(str(activity))
                            + "</u>"
                            + (":<br>" if invited_counter else "")
                            + escape(", ".join(persons_invited))
                        )

                        # Message about persons that are already participating in activity:
                        already_participating_text = ""
                        if len(persons_already_participant) > 0:
                            already_participating_text = (
                                "<br><u>"
                                + str(len(persons_already_participant))
                                + " deltager allerede:</u><br> "
                                + escape(", ".join(persons_already_participant))
                            )

                        # Message about persons that are already invited (and not found as participant)
                        already_invited_text = ""
                        if len(persons_already_invited) > 0:
                            already_invited_text = (
                                "<br><u>"
                                + str(len(persons_already_invited))
                                + " er allerede inviteret:</u><br> "
                                + escape(", ".join(persons_already_invited))
                            )

                        # Message about person too young to get invited:
                        persons_too_young_text = ""
                        if len(persons_too_young) > 0:
                            persons_too_young_text = (
                                "<br><u>"
                                + str(len(persons_too_young))
                                + " er under minimumsalder for aktiviteten "
                                + "("
                                + str(activity.min_age)
                                + " år)"
                                + ":</u><br> "
                                + escape(", ".join(persons_too_young))
                            )

                        # Message about person too old to get invited:
                        persons_too_old_text = ""
                        if len(persons_too_old) > 0:
                            persons_too_old_text = (
                                "<br><u>"
                                + str(len(persons_too_old))
                                + " er over maximumsalder for aktiviteten "
                                + "("
                                + str(activity.max_age)
                                + " år) "
                                + ":</u><br> "
                                + escape(", ".join(persons_too_old))
                            )

                        # Message about persons that have the dont_send_mails flag set
                        persons_dont_send_mails_text = ""
                        if len(persons_dont_send_mails) > 0:
                            persons_dont_send_mails_text = (
                                "<br><u>"
                                + str(len(persons_dont_send_mails))
                                + " har valgt ikke at modtage mails:</u><br> "
                                + escape(", ".join(persons_dont_send_mails))
                            )

                        # Show message to user
                        messages.success(
                            request,
                            mark_safe(
                                invited_text
                                + already_participating_text
                                + already_invited_text
                                + persons_too_young_text
                                + persons_too_old_text
                                + persons_dont_send_mails_text,
                            ),
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
        "Inviter valgte personer til en aktivitet"
    )

    def create_volunteer_action(modelAdmin, request, queryset):
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
            modelAdmin.message_user(
                request,
                "Du må kun vælge én post ad gangen for at oprette en frivillig.",
                level="error",
            )
            return HttpResponseRedirect(request.get_full_path())

        selected_obj = queryset.first()
        person = getattr(selected_obj, "person", selected_obj)

        if person is None:
            modelAdmin.message_user(
                request,
                "Den valgte post kan ikke bruges til at oprette en frivillig.",
                level="error",
            )
            return HttpResponseRedirect(request.get_full_path())

        context = admin.site.each_context(request)
        context["person"] = person
        context["queryset"] = queryset
        context["action_name"] = "create_volunteer_action"

        initial = {}
        if hasattr(selected_obj, "start_date"):
            initial["start_date"] = selected_obj.start_date or timezone.now().date()
        if hasattr(selected_obj, "end_date"):
            initial["end_date"] = selected_obj.end_date

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

                modelAdmin.message_user(
                    request,
                    f"{person.name} er oprettet som frivillig og afventer brugerens godkendelse.",
                )
                return HttpResponseRedirect(request.get_full_path())
        else:
            context["create_volunteer_form"] = CreateVolunteerForm(initial=initial)

        return render(
            request,
            "admin/create_volunteer.html",
            context,
        )

    create_volunteer_action.short_description = "Anmod person om at blive frivillig"
    create_volunteer_action.allowed_permissions = ("view",)

    def export_participants_csv(self, request, queryset):
        print(f"queryset:[{queryset}]")
        if queryset.model is Activity:
            activities = [a.pk for a in queryset]
            participants = ActivityParticipant.objects.filter(activity__in=activities)
        elif queryset.model is ActivityParticipant:
            participants = queryset

        context = admin.site.each_context(request)
        context["participants"] = participants
        context["queryset"] = queryset

        result_string = """"Forening"; "Afdeling"; "Aktivitet"; "Navn";\
            "Alder"; "Køn"; "Post-nr"; "Betalingsinfo"; "forældre navn";\
            "forældre email"; "forældre tlf"; "Foto-tilladelse";\
            "Note til arrangørerne"\n"""
        for p in participants:
            gender = p.person.gender_text()

            parent = p.person.family.get_first_parent()
            if parent:
                parent_name = parent.name
                parent_phone = parent.phone
                if not p.person.family.dont_send_mails:
                    parent_email = parent.email
                else:
                    parent_email = ""
            else:
                parent_name = ""
                parent_phone = ""
                parent_email = ""

            if p.photo_permission == "OK":
                photo = "Tilladelse givet"
            else:
                photo = "Ikke tilladt"

            result_string = (
                result_string
                + p.activity.department.union.name
                + ";"
                + p.activity.department.name
                + ";"
                + p.activity.name
                + ";"
                + p.person.name
                + ";"
                + str(p.person.age_years())
                + ";"
                + gender
                + ";"
                + p.person.zipcode
                + ";"
                + str(p.payment_info(False))
                + ";"
                + parent_name
                + ";"
                + parent_email
                + ";"
                + parent_phone
                + ";"
                + photo
                + ";"
                + '"'
                + p.note.replace('"', '""')
                + '"'
                + "\n"
            )
        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("utf-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="deltagere.csv"'
        return response

    export_participants_csv.short_description = "Eksporter deltagerliste (CSV)"
