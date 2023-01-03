from datetime import timedelta

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.widgets import AdminDateWidget
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe


from members.models import (
    Activity,
    ActivityInvite,
    Department,
    Person,
)

from .person_admin import (
    PersonAdmin
)


class WaitingListDepartmentFilter(admin.SimpleListFilter):
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
            return queryset.filter(department__pk=self.value())
        

class WaitingListAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = "Venteliste"
        verbose_name_plural = "Ventelister"
    
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["image"].help_text = "og noget hjælpetext"
        return form

    list_display = (
        "id",
        "department_link",
        "person_link",
        "person_age_years",
        "person_gender_text",
        "user_created",
        "user_added_waiting_list",
    )

# GEM knappen skal ændres til "Slet fra venteliste og send email" ??

    list_filter = (
        WaitingListDepartmentFilter,
        #"person__gender",
    )

    actions = [
        "invite_many_to_activity_action", 
        "delete_many_from_department_waitinglist"]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def invite_many_to_activity_action(self, request, queryset):
        return PersonAdmin.invite_many_to_activity_action(self, request, queryset)
    invite_many_to_activity_action.short_description = "Inviter alle valgte til en aktivitet"

    def delete_many_from_department_waitinglist(self, request, queryset):
        # User has selected one or more records from the overview
        # Confirm by select one department
        # and enter a text line to be included in standard email
        # And also select the right option 
        # This means: All families / persons will get an email
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_persons"
        ):
            department_list_query = Department.objects.all()
        else:
            department_list_query = Department.objects.filter(
                adminuserinformation__user=request.user
            )
        department_list = [("-","-")]
        for department in department_list_query:
            department_list.append((department.id, department.name))

        confirm_list = [("-", "-")]
        confirm_list.append((1, "Ja - fjern person(er) fra venteliste for den valgte afdeling og send email til dem med info"))
        confirm_list.append((2, "Nej - fjern ikke personer(er) fra venteliste for den valgte afdeling"))

        # Form used to confirm department, confirm action and write additional message to be in email
        class MassConfirmForm(forms.Form):
            department = forms.ChoiceField(label="Afdeling", choices=department_list)
            email_text = forms.CharField(label="Email ekstra info", widget=forms.Textarea)
            confirmation = forms.ChoiceField(label="Bekræft", choices=confirm_list)
            
        persons = queryset

        context = admin.site.each_context(request)
        context["persons"] = persons
        context["queryset"] = queryset

        if request.method == "POST" and "confirmation" in request.POST:
            # Post request with data
            mass_confirmation_form = MassConfirmForm(request.POST)
            context["mass_confirmation_form"] = mass_confirmation_form

            if (
                mass_confirmation_form.is_valid()
                and mass_confirmation_form.cleaned_data["department"] != "-"
                and mass_confirmation_form.cleaned_data["confirmation"] == 1
            ):
                messages.error(
                    request, 
                    "Så vidt så godt"
                )
            else:
                messages.error(
                    request,
                    "ikke godkenddt"
                )
        else:
            context["mass_confirmation_form"] = MassConfirmForm()

        return render(request, "admin/delete_many_from_waitinglist.html", context)

    delete_many_from_department_waitinglist.short_description = "Fjern fra venteliste" 

    def get_queryset(self, request):
        return super().get_queryset(request)

    def department_link(self, item):
        url = reverse("admin:members_department_change", args=[item.department_id])
        link = '<a href="%s">%s</a>' % (url, item.department.name)
        return mark_safe(link)


    department_link.short_description = "Afdeling"
    department_link.admin_order_field = "department__name"

    def person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.person_id])
        link = '<a href="%s">%s</a>' % (url, item.person.name)
        return mark_safe(link)

    person_link.short_description = "Person"
    person_link.admin_order_field = "person__name"

    def person_age_years(self, item):
        return item.person.age_years()

    person_age_years.short_description = "Alder"
    person_age_years.admin_order_field = "-person__birthday"

    def person_gender_text(self, item):
        if item.person.gender == "MA":
            return "Dreng"
        elif item.person.gender == "FM":
            return "Pige"
        else:
            return "Andet"

    person_gender_text.short_description = "Køn"
    person_gender_text.admin_order_field = "persongendertext"


    def user_created(self, item):
        return item.on_waiting_list_since
    user_created.short_description = "Person oprettet"
    user_created.admin_order_field = "on_waiting_list_since"

    def user_added_waiting_list(self, item):
        return item.added_at
    user_added_waiting_list.short_description = "Tilføjet til venteliste"
    user_added_waiting_list.admin_order_field = "added_at"
