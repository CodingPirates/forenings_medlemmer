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

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)

        # Following will hide superusers for normal admins !
        # if not request.user.is_superuser:
        #    return qs.filter(is_superuser=False)
        return qs

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ["is_staff", "is_superuser", "is_active", "groups__id"]
        else:
            return ["is_staff", "is_active", "groups__id"]
