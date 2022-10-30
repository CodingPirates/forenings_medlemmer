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

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
    )

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)

        # Following will hide superusers for normal admins !
        # if not request.user.is_superuser:
        #    return qs.filter(is_superuser=False)
        return qs

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ["is_staff", "is_superuser", "is_active"]
        else:
            return ["is_staff", "is_active"]

    # Note 20221030 by MHewel: get_list_filter could also return "groups__id", but this is id of group. Disabled for now, have to find a way to show group name
