from django.contrib import admin
from django.db.models.functions import Upper
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from members.models import AdminUserInformation, Person, Union, Department


class AdminUserInformationInline(admin.StackedInline):
    model = AdminUserInformation
    filter_horizontal = ("departments", "unions")
    can_delete = False

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "departments":
            kwargs["queryset"] = Department.objects.all().order_by(Upper("name").asc())
        if db_field.name == "unions":
            kwargs["queryset"] = Union.objects.all().order_by(Upper("name").asc())
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class PersonInline(admin.StackedInline):
    model = Person
    fields = ("name",)
    readonly_fields = ("name",)


class AdminUserGroupListFilter(admin.SimpleListFilter):
    title = "Grupper"
    parameter_name = "group"

    def lookups(self, request, model_admin):
        groupList = [("none", "(ingen gruppe)")]
        for aGroup in Group.objects.all().order_by("name"):
            groupList += (
                (
                    str(aGroup.id),
                    str(aGroup.name),
                ),
            )
        return groupList

    def queryset(self, request, queryset):
        group_id = request.GET.get(self.parameter_name, None)
        if group_id == "none":
            return queryset.filter(groups__isnull=True)
        if group_id:
            return queryset.filter(groups=group_id)
        return queryset


class AdminUserUnionListFilter(admin.SimpleListFilter):
    title = "Forening"
    parameter_name = "union"

    def lookups(self, request, model_admin):
        unionList = [("none", "(ingen forening)"), ("any", "(mindst en forening)")]
        for aUnion in Union.objects.all().order_by("name"):
            unionList += (
                (
                    str(aUnion.id),
                    str(aUnion.name),
                ),
            )
        return unionList

    def queryset(self, request, queryset):
        union_id = request.GET.get(self.parameter_name, None)
        if union_id == "none":
            return queryset.filter(adminuserinformation__unions__isnull=True)
        elif union_id == "any":
            return queryset.exclude(adminuserinformation__unions__isnull=True)
        elif union_id:
            return queryset.filter(adminuserinformation__unions=union_id)
        return queryset


class AdminUserDepartmentListFilter(admin.SimpleListFilter):
    title = "Afdeling"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        departmentList = [("none", "(ingen afdeling)"), ("any", "(mindst en afdeling)")]
        for aDepartment in Department.objects.all().order_by("name"):
            departmentList += (
                (
                    str(aDepartment.id),
                    str(aDepartment.name),
                ),
            )
        return departmentList

    def queryset(self, request, queryset):
        department_id = request.GET.get(self.parameter_name, None)
        if department_id == "none":
            return queryset.filter(adminuserinformation__departments__isnull=True)
        elif department_id == "any":
            return queryset.exclude(adminuserinformation__departments__isnull=True)
        if department_id:
            return queryset.filter(adminuserinformation__departments=department_id)
        return queryset


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

    readonly_fields = ["date_joined", "last_login"]

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)

        # Following will hide superusers for normal admins !
        # if not request.user.is_superuser:
        #    return qs.filter(is_superuser=False)
        return qs

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return [
                "is_staff",
                "is_superuser",
                "is_active",
                AdminUserGroupListFilter,
                AdminUserUnionListFilter,
                AdminUserDepartmentListFilter,
            ]
        else:
            return [
                "is_staff",
                "is_active",
                AdminUserGroupListFilter,
                AdminUserUnionListFilter,
                AdminUserDepartmentListFilter,
            ]

    def get_fieldsets(self, request, obj=None):
        # 20230924: https://stackoverflow.com/questions/16102222/djangoremove-superuser-checkbox-from-django-admin-panel-when-login-staff-users
        if not obj:
            return self.add_fieldsets

        perm_fields = ("is_active", "is_staff", "groups")

        if request.user.is_superuser:
            perm_fields = (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )

        return [
            (None, {"fields": ("username", "password")}),
            (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
            (("Permissions"), {"fields": perm_fields}),
            (("Important dates"), {"fields": ("last_login", "date_joined")}),
        ]
