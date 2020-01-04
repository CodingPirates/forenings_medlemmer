from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from members.models import AdminUserInformation, Person


class AdminUserInformationInline(admin.StackedInline):
    model = AdminUserInformation
    filter_horizontal = ("departments", "unions")
    can_delete = False


class PersonInline(admin.StackedInline):
    model = Person
    fields = ("name",)
    readonly_fields = ("name",)


class UserAdmin(UserAdmin):
    inlines = (AdminUserInformationInline, PersonInline)
