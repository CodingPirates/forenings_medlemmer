import codecs
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import connection
from django.http import HttpResponse
from django.utils import timezone
from collections import namedtuple
from members.models import AdminUserInformation, Person


def namedtuplefetchall(cursor):
    desc = cursor.description
    res = namedtuple("Result", [col[0] for col in desc])
    return [res(*row) for row in cursor.fetchall()]


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

    actions = ["export_obsolete_admins"]

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

    def export_obsolete_admins(self, request, queryset):
        # This function is only made as an example of how  to get additional data for unions
        result_string = 'Bruger,Sidste login,Type,Navn,Lukkedato,Info\n'

        for p in queryset:
            with connection.cursor() as cursor:
                cursor.execute(
                    " SELECT au.username, "
                    + "   DATE(au.last_login) AS user_lastlogin, "
                    + "   'Forening' AS type, "
                    + "   mu.name, "
                    + "   DATE(mu.closed_at) AS closedate, "
                    + "   'Brugeren er Admin og har adgang til en lukket forening' AS info "
                    + " FROM auth_user AS au, "
                    + "   members_adminuserinformation AS ma, "
                    + "   members_adminuserinformation_unions AS mau, "
                    + "   members_union mu "
                    + " WHERE au.id = "
                    + str(p.id)
                    + "   AND au.id = ma.user_id "
                    + "   AND au.is_staff = true "
                    + "   AND au.is_superuser = false "
                    + "   AND mau.adminuserinformation_id = ma.id "
                    + "   AND mu.id = mau.union_id "
                    + "   AND mu.closed_at is NOT NULL "
                    + "   AND mu.closed_at < '"
                    + str(timezone.now().date())
                    + "'"
                    + " UNION "
                    + " SELECT au.username, "
                    + "   DATE(au.last_login) AS user_lastlogin, "
                    + "   'Afdeling' AS type, "
                    + "   md.name, "
                    + "   DATE(md.closed_dtm) AS closedate, "
                    + "   'Brugeren er Admin og har adgang til en lukket afdeling' AS info "
                    + " FROM auth_user AS au, "
                    + "   members_adminuserinformation AS ma, "
                    + "   members_adminuserinformation_departments AS mad, "
                    + "   members_department md "
                    + " WHERE au.id = "
                    + str(p.id)
                    + "   AND au.id = ma.user_id "
                    + "   AND au.is_staff = true "
                    + "   AND au.is_superuser = false "
                    + "   AND mad.adminuserinformation_id = ma.id "
                    + "   AND md.id = mad.department_id "
                    + "   AND md.closed_dtm is NOT NULL "
                    + "   AND md.closed_dtm < '"
                    + str(timezone.now().date())
                    + "'"
                    + " UNION "
                    + " SELECT au.username, "
                    + "   DATE(au.last_login) AS user_lastlogin, "
                    + "   ' ' AS type, "
                    + "   ' ' AS name,  "
                    + "   ' ' AS closedate, "
                    + "   'Brugeren er Admin og har hverken adgang til foreninger eller afdelinger' AS info "
                    + " FROM auth_user AS au, "
                    + "   members_adminuserinformation AS ma "
                    " WHERE au.id = "
                    + str(p.id)
                    + "   AND au.is_staff = true "
                    + "   AND au.is_superuser = false "
                    + "   AND ma.user_id = au.id "
                    + "   AND ma.id NOT IN "
                    + "   ( SELECT DISTINCT x.adminuserinformation_id "
                    + "     FROM "
                    + "     ( SELECT adminuserinformation_id "
                    + "       FROM members_adminuserinformation_unions "
                    + "       UNION "
                    + "       SELECT adminuserinformation_id "
                    + "       FROM members_adminuserinformation_departments "
                    + "     ) AS x "
                    + "   ) "
                    + " ORDER BY  username "
                )
                results = namedtuplefetchall(cursor)
                for r in results:
                    result_string = (
                        result_string
                        + r.username
                        + ","
                        + r.user_lastlogin
                        + ","
                        + r.type
                        + ","
                        + r.name
                        + ","
                        + r.closedate
                        + ","
                        + r.info
                        + "\n"
                    )
        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("utf-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="obsolete-admins.csv"'
        return response

    export_obsolete_admins.short_description = "CSV Export: Ugyldige admins"
