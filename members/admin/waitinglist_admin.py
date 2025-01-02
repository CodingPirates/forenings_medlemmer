from django import forms
from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape

from members.models import Union, Department, AdminUserInformation, Municipality

import members.models.emailtemplate

# import members.admin.admin_actions
from members.admin.admin_actions import AdminActions


class person_waitinglist_union_filter(admin.SimpleListFilter):
    title = "Forening"
    parameter_name = ""

    def lookups(self, request, model_admin):
        unions = []
        for union in AdminUserInformation.get_unions_admin(request.user).order_by(
            "name"
        ):
            unions.append((str(union.pk), union.name))

        return unions

    def queryset(self, request, queryset):
        if self.value() == "any":
            return queryset.exclude(department__union__isnull=True)
        elif self.value() == "none":
            return queryset.filter(department__union__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(department__union__id=self.value())


class person_waitinglist_department_filter(admin.SimpleListFilter):
    title = "Afdeling"
    parameter_name = "waiting_list"

    def lookups(self, request, model_admin):
        departments = []
        for department in AdminUserInformation.get_departments_admin(
            request.user
        ).order_by("name"):
            departments.append((str(department.pk), department.name))

        return departments

    def queryset(self, request, queryset):
        if self.value() == "any":
            return queryset.exclude(department__isnull=True)
        elif self.value() == "none":
            return queryset.filter(department__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(department__id=self.value())


class person_waitinglist_municipality_filter(admin.SimpleListFilter):
    title = "Kommune"
    parameter_name = "person__municipality"

    def lookups(self, request, model_admin):
        # loop through the persons in waitinglist, and get the municipality values for the filter
        municipalities = [("any", "(Med kommune)"), ("none", "(Uden kommune)")]
        municipality_ids = model_admin.model.objects.values_list(
            "person__municipality__id", flat=True
        ).distinct()
        for municipality in Municipality.objects.filter(
            id__in=municipality_ids
        ).order_by("name"):
            municipalities.append((str(municipality.pk), municipality.name))
        return municipalities

    def queryset(self, request, queryset):
        if self.value() == "any":
            return queryset.exclude(person__municipality__isnull=True)
        elif self.value() == "none":
            return queryset.filter(person__municipality__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(person__municipality__id=self.value())


class WaitingListAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = "Venteliste"
        verbose_name_plural = "Ventelister"

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        return form

    list_display = (
        "department_link",
        "person_link",
        "person_age_years",
        "person_gender_text",
        "zipcode",
        "municipality",
        "user_waiting_list_number",
        "user_created",
        "user_added_waiting_list",
        "union_link",
    )

    list_filter = (
        person_waitinglist_union_filter,
        person_waitinglist_department_filter,
        person_waitinglist_municipality_filter,
        "person__gender",
    )

    search_fields = [
        "department__name",
        "department__union__name",
        "person__name",
        "person__zipcode",
        "person__municipality__name",
    ]
    search_help_text = mark_safe(
        """Du kan søge på forening (navn), afdeling (navn) eller person (navn, postnummer eller kommune).<br>
        'Nummer på venteliste' er relateret til personernes oprettelsestidspunkt"""
    )

    actions = [
        "delete_many_from_department_waitinglist_action",
        AdminActions.invite_many_to_activity_action,
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def delete_many_from_department_waitinglist_action(self, request, queryset):
        # User has selected one or more records from the waitinglist overview
        # User can only delete persons from waiting list from one department
        # and user can max delete 50 persons at the same time
        # Confirm by select one department (that must match the entries selected)
        # and enter a text line to be included in standard email
        # (can it show the mail template ?)
        # And also select the right option
        # This means: All families / persons will get an email with information
        template = members.models.emailtemplate.EmailTemplate.objects.get(
            idname="WAITING_LIST_DEL"
        )

        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_persons"
        ):
            department_list_query = Department.objects.all().order_by("name")
        else:
            department_list_query = Department.objects.filter(
                adminuserinformation__user=request.user
            ).order_by("name")

        waitinglist_departments = []  # List of unique departments selected by user
        for item in queryset:
            if not waitinglist_departments.count(item.department):
                waitinglist_departments.append(item.department)

        department_list = [("-", "-")]
        for department in department_list_query:
            department_list.append((department.id, department.name))

        confirm_list = [(0, "Bekræft sletning fra venteliste")]
        confirm_list.append(
            (
                1,
                "Ja - fjern person(er) fra venteliste for den valgte afdeling og send email til dem med info",
            )
        )
        confirm_list.append(
            (2, "Nej - fjern ikke personer(er) fra venteliste for den valgte afdeling")
        )

        # Form used to confirm department, confirm action and write additional message to be in email
        class MassConfirmForm(forms.Form):
            department = forms.ChoiceField(label="Afdeling", choices=department_list)
            email_text = forms.CharField(
                label="Email ekstra info", widget=forms.Textarea
            )
            confirmation = forms.ChoiceField(label="Bekræft", choices=confirm_list)

        persons = queryset

        context = admin.site.each_context(request)
        context["persons"] = persons
        context["queryset"] = queryset
        context["departments"] = waitinglist_departments
        context["emailtemplate"] = template
        email_info = ""

        if request.method == "POST" and "confirmation" in request.POST:
            # Post request with data

            mass_confirmation_form = MassConfirmForm(request.POST)
            context["mass_confirmation_form"] = mass_confirmation_form
            if (
                len(waitinglist_departments) == 1
                and len(queryset) <= 50
                and len(queryset) >= 1
            ):
                if (
                    mass_confirmation_form.is_valid()
                    and mass_confirmation_form.cleaned_data["department"] != "-"
                    and mass_confirmation_form.cleaned_data["confirmation"] == "1"
                ):
                    department_confirmed = mass_confirmation_form.cleaned_data[
                        "department"
                    ]
                    if str(department_confirmed) == str(waitinglist_departments[0].id):
                        # All confirmed - ready to go
                        email_info = mass_confirmation_form.cleaned_data["email_text"]
                        wl = []
                        persons_deleted_from_wl = 0
                        try:
                            with transaction.atomic():
                                footer = f"[{str(timezone.now())}]"
                                for wl in queryset:
                                    mail_context = {
                                        "department": wl.department,
                                        "person": wl.person,
                                        "email_extra_info": email_info,
                                        "footer": footer,
                                    }
                                    if wl.person.email and (
                                        wl.person.email != wl.person.family.email
                                    ):
                                        # If person got own email then also send to that
                                        template.makeEmail(
                                            [wl.person, wl.person.family],
                                            mail_context,
                                            True,
                                        )
                                    else:
                                        template.makeEmail(
                                            wl.person.family, mail_context, True
                                        )
                                    wl.delete()
                                    persons_deleted_from_wl += 1

                        except Exception:
                            messages.error(
                                request,
                                "Fejl - ingen person blev slettet fra venteliste. Der var problemer med "
                                + (wl.person.name if wl else "(n/a)")
                                + ". Vær sikker på at personen ikke allerede er slettet. ",
                            )
                            return
                        messages.success(
                            request,
                            f"Det blev slettet {persons_deleted_from_wl} fra ventelisten til afdeling {waitinglist_departments[0]}",
                        )
                        return

                    else:
                        messages.error(
                            request,
                            "Valgte afdeling stemmer ikke overens med afdelingen for de personer der er valgt.",
                        )
                        return

                else:
                    messages.error(request, "ikke godkendt")
                    return

            else:
                messages.error(
                    request,
                    "Du må kun fjerne personer fra en afdeling ad gangen, og vælge mellem 1 og 50 personer",
                )
                return
        else:
            context["mass_confirmation_form"] = MassConfirmForm()

        return render(request, "admin/delete_many_from_waitinglist.html", context)

    delete_many_from_department_waitinglist_action.short_description = (
        "Fjern fra venteliste"
    )

    def get_queryset(self, request):
        qs = super(WaitingListAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_persons"
        ):
            return qs
        departments = Department.objects.filter(adminuserinformation__user=request.user)
        unions = Union.objects.filter(adminuserinformation__user=request.user)

        return qs.filter(
            Q(department__in=departments) | Q(department__union__in=unions)
        ).distinct()

    def union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.department.union_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.department.union.name))
        return mark_safe(link)

    union_link.short_description = "Forening"
    union_link.admin_order_field = "department__union__name"

    def department_link(self, item):
        url = reverse("admin:members_department_change", args=[item.department_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.department.name))
        return mark_safe(link)

    department_link.short_description = "Afdeling"
    department_link.admin_order_field = "department__name"

    def person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.person_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.person.name))
        return mark_safe(link)

    person_link.short_description = "Person"
    person_link.admin_order_field = "person__name"

    def person_age_years(self, item):
        return item.person.age_years()

    person_age_years.short_description = "Alder"
    person_age_years.admin_order_field = "-person__birthday"

    def person_gender_text(self, item):
        return item.person.gender_text()

    person_gender_text.short_description = "Køn"
    person_gender_text.admin_order_field = "person__gender"

    def user_created(self, item):
        return item.on_waiting_list_since

    user_created.short_description = "Person oprettet"
    user_created.admin_order_field = "on_waiting_list_since"

    def user_added_waiting_list(self, item):
        return item.added_at

    user_added_waiting_list.short_description = "Tilføjet til venteliste"
    user_added_waiting_list.admin_order_field = "added_at"

    def user_waiting_list_number(self, item):
        return item.number_on_waiting_list()

    user_waiting_list_number.short_description = "Ventelistenummer"
    user_waiting_list_number.admin_order_field = "on_waiting_list_since"

    def zipcode(self, item):
        return item.person.zipcode

    zipcode.short_description = "Post nr"
    zipcode.admin_order_field = "person__zipcode"

    def municipality(self, item):
        if item.person.municipality is None:
            return ""
        return item.person.municipality.name

    municipality.short_description = "Kommune"
    municipality.admin_order_field = "person__municipality__name"
