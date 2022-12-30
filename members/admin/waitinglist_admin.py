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

    list_display = (
        "id",
        "department_link",
        "person_link",
        "person_age_years",
        "UserCreated",
        "UserAddedWaitingList",
    )

    list_filter = (
        WaitingListDepartmentFilter,
    )

    actions = ["invite_many_to_activity_action", ]

    def invite_many_to_activity_action(self, request, queryset):
        return PersonAdmin.invite_many_to_activity_action(self, request, queryset)

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

    def UserCreated(self, item):
        return item.on_waiting_list_since
    UserCreated.short_description = "Person oprettet"

    def UserAddedWaitingList(self, item):
        return item.added_at
    UserAddedWaitingList.short_description = "Tilføjet til venteliste"
