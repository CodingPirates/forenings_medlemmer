import codecs
from django.contrib import admin
from django.db.models.functions import Upper
from django.urls import reverse
from django.utils.safestring import mark_safe
from members.models import (
    Union,
    Address,
    Person,
    Activity,
    AdminUserInformation,
)
from django.utils.html import escape
from django.http import HttpResponse
from django.db.models import Count


class AdminUserDepartmentInline(admin.TabularInline):
    model = AdminUserInformation.departments.through

    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    classes = ["hideheader"]

    extra = 0
    verbose_name = "Admin Bruger"
    verbose_name_plural = "Admin Brugere"

    fields = (
        "user_username",
        "user_first_name",
        "user_last_name",
        "user_email",
        "user_last_login",
    )
    readonly_fields = (
        "user_username",
        "user_first_name",
        "user_last_name",
        "user_email",
        "user_last_login",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filter out inactive users and non-staff users
        return qs.filter(
            adminuserinformation__user__is_active=True,
            adminuserinformation__user__is_staff=True,
        ).select_related("adminuserinformation__user")

    def user_username(self, instance):
        return instance.adminuserinformation.user.username

    user_username.short_description = "Brugernavn"

    def user_first_name(self, instance):
        return instance.adminuserinformation.user.first_name

    user_first_name.short_description = "Fornavn"

    def user_last_name(self, instance):
        return instance.adminuserinformation.user.last_name

    user_last_name.short_description = "Efternavn"

    def user_email(self, instance):
        return instance.adminuserinformation.user.email

    user_email.short_description = "Email"

    def user_last_login(self, instance):
        return instance.adminuserinformation.user.last_login.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    user_last_login.short_description = "Sidste login"

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UnionDepartmentFilter(admin.SimpleListFilter):
    title = "Forening"
    parameter_name = "Union"

    def lookups(self, request, model_admin):
        return [(str(union.pk), str(union.name)) for union in Union.objects.all()]

    def queryset(self, request, queryset):
        return queryset if self.value() is None else queryset.filter(union=self.value())


class DepartmentAdmin(admin.ModelAdmin):
    inlines = [AdminUserDepartmentInline]
    list_display = (
        "department_link",
        "address",
        "department_email",
        "isVisible",
        "isOpening",
        "has_waiting_list",
        "created",
        "closed_dtm",
        "waitinglist_count_link",
        "department_union_link",
    )
    list_filter = (
        "address__region",
        UnionDepartmentFilter,
        "isVisible",
        "isOpening",
        "created",
        "closed_dtm",
        "has_waiting_list",
    )
    autocomplete_fields = ("union",)
    raw_id_fields = ("union",)
    search_fields = (
        "name",
        "union__name",
        "department_email",
        "address__streetname",
        "address__housenumber",
        "address__placename",
        "address__zipcode",
        "address__city",
    )
    search_help_text = (
        "Du kan søge på afdeling (navn, adresse, email) eller forening (navn)"
    )

    ordering = ["name"]
    filter_horizontal = ["department_leaders"]

    actions = [
        "export_department_info_csv",
    ]

    # Solution found on https://stackoverflow.com/questions/57056994/django-model-form-with-only-view-permission-puts-all-fields-on-exclude
    # formfield_for_foreignkey described in documentation here: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.formfield_for_foreignkey
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "address":
            kwargs["queryset"] = Address.get_user_addresses(request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "department_leaders":
            kwargs["queryset"] = Person.objects.filter(user__is_staff=True).order_by(
                Upper("name")
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        qs = queryset.annotate(waitinglist_count=Count("waitinglist"))

        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
            return qs
        return qs.filter(adminuserinformation__user=request.user)

    fieldsets = [
        (
            "Beskrivelse",
            {
                "fields": ("name", "union", "description", "open_hours"),
                "description": "<p>Lav en beskrivelse af jeres aktiviteter, teknologier og tekniske niveau.</p><p>Åbningstid er ugedag samt tidspunkt<p>",
            },
        ),
        (
            "Ansvarlig",
            {"fields": ("responsible_name", "department_email", "department_leaders")},
        ),
        (
            "Adresse",
            {"fields": ("address",)},
        ),
        (
            "Afdelingssiden",
            {
                "fields": ("website", "isOpening", "isVisible"),
                "description": "<p>Har kan du vælge om afdeling skal vises på codingpirates.dk/afdelinger og om der skal være et link til en underside</p>",
            },
        ),
        (
            "Yderlige data",
            {
                "fields": ("has_waiting_list", "created", "closed_dtm"),
                "description": "<p>Venteliste betyder at børn har mulighed for at skrive sig på ventelisten (tilkendegive interesse for denne afdeling). Den skal typisk altid være krydset af.</p>",
                "classes": ("collapse",),
            },
        ),
    ]

    def department_union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.union_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.union.name))
        return mark_safe(link)

    department_union_link.short_description = "Forening"
    department_union_link.admin_order_field = "union__name"

    def department_link(self, item):
        url = reverse("admin:members_department_change", args=[item.id])
        link = '<a href="%s">%s</a>' % (url, escape(item.name))
        return mark_safe(link)

    department_link.short_description = "Afdeling"
    department_link.admin_order_field = "name"

    def waitinglist_count_link(self, item):
        admin_url = reverse("admin:members_waitinglist_changelist")
        link = f"""<a
            href="{admin_url}?waiting_list={item.id}"
            title="Vis venteliste for afdelingen Coding Pirates {item.name}">
            {item.waitinglist_count}
            </a>"""
        return mark_safe(link)

    waitinglist_count_link.short_description = "Venteliste"
    waitinglist_count_link.admin_order_field = "waitinglist_count"

    def export_department_info_csv(self, request, queryset):
        result_string = '"Forening"; "Afdeling"; "Email"; '
        result_string += '"Afdeling-Startdato"; "Afdeling-lukkedato"; '
        result_string += '"Kaptajn"; "Kaptajn-email"; "Kaptajn-telefon"; '
        result_string += '"Adresse"; "Post#"; "By"; "Region"; '
        result_string += '"Dato-sidste-forløb"; "Dato-sidste-arrangement"; '
        result_string += (
            '"Dato-sidste-foreningsmedlemskab"; "Dato-sidste-støttemedlemskab"\n'
        )

        # There can be multiple departmentleaders (or even none)

        for d in queryset.order_by("name"):
            info1 = d.union.name + ";"
            info1 += d.name + ";"
            info1 += d.department_email + ";"
            if d.created is not None:
                info1 += d.created.strftime("%Y-%m-%d")
            info1 += ";"
            if d.closed_dtm is not None:
                info1 += d.closed_dtm.strftime("%Y-%m-%d")
            info1 += ";"
            info2 = d.address.streetname
            if d.address.housenumber != "":
                info2 += " " + d.address.housenumber
            if d.address.floor != "" or d.address.door != "":
                info2 += ", "
            if d.address.floor != "":
                info2 += d.address.floor + "."
            if d.address.door != "":
                info2 += d.address.door
            info2 += ";"
            info2 += d.address.zipcode + ";"
            info2 += d.address.city + ";"
            info2 += d.address.region + ";"

            info2 += GetLastDate(d, "FORLØB") + ";"
            info2 += GetLastDate(d, "ARRANGEMENT") + ";"
            info2 += GetLastDate(d, "FORENINGSMEDLEMSKAB") + ";"
            info2 += GetLastDate(d, "STØTTEMEDLEMSKAB") + ";"

            leaders = d.department_leaders.all().order_by("name")

            if leaders.count() == 0:
                result_string += info1 + ";;;" + info2 + "\n"
            else:
                for leader in leaders:
                    result_string += info1
                    result_string += leader.name + ";"
                    result_string += leader.email + ";"
                    result_string += leader.phone + ";"
                    result_string += info2 + "\n"

        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("utf-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="afdelingsinfo.csv"'
        return response

    export_department_info_csv.short_description = "Exporter Afdelingsinfo (CSV)"


def GetLastDate(department_id, activity_type):
    last_activity = (
        Activity.objects.all()
        .filter(department=department_id, activitytype=activity_type)
        .order_by("-start_date")
        .first()
    )
    return (
        "" if last_activity is None else last_activity.start_date.strftime("%Y-%m-%d")
    )
