import codecs
import csv
from django.conf import settings
from django.contrib import admin
from django.db.models.functions import Upper
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.html import escape
from io import StringIO
from members.models import Address, Person, Department, AdminUserInformation

from django.db.models import Count


def generate_union_csv(queryset):
    output = StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\n")

    header = [
        "Forening",
        "Email",
        "Oprettelsdato",
        "Lukkedato",
        "CVR",
        "formand-navn",
        "formand-email",
        "formand-tlf",
        "næstformand-navn",
        "næstformand-email",
        "næstformand-tlf",
        "kasserer-navn",
        "kasserer-email",
        "kasserer-tlf",
        "sekretær-navn",
        "sekretær-email",
        "sekretær-tlf",
    ]
    writer.writerow(header)

    def person_fields(person):
        if person is None:
            return ["", "", ""]
        return [
            getattr(person, "name", ""),
            getattr(person, "email", ""),
            getattr(person, "phone", ""),
        ]

    for union in queryset:
        row = [
            union.name,
            union.email,
            union.founded_at.strftime("%Y-%m-%d") if union.founded_at else "",
            union.closed_at.strftime("%Y-%m-%d") if union.closed_at else "",
            union.cvr.strip() if union.cvr else "",
            *person_fields(getattr(union, "chairman", None)),
            *person_fields(getattr(union, "second_chair", None)),
            *person_fields(getattr(union, "cashier", None)),
            *person_fields(getattr(union, "secretary", None)),
        ]
        writer.writerow(row)

    return output.getvalue()


class AdminUserUnionInline(admin.TabularInline):
    model = AdminUserInformation.unions.through

    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    classes = ["hideheader"]

    extra = 0
    verbose_name = "Admin Bruger"
    verbose_name_plural = "Admin Brugere"
    list_per_page = settings.LIST_PER_PAGE
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


class UnionAdmin(admin.ModelAdmin):
    inlines = [AdminUserUnionInline]
    list_display = (
        "union_link",
        "address",
        "email",
        "founded_at",
        "closed_at",
        "waitinglist_count_link",
        "has_cvr_number",
    )
    list_filter = (
        "address__region",
        "founded_at",
        "closed_at",
    )
    search_fields = (
        "name",
        "email",
        "address__streetname",
        "address__housenumber",
        "address__placename",
        "address__zipcode",
        "address__city",
    )
    search_help_text = "Du kan søge på forening (navn, adresse, email)"

    filter_horizontal = ["board_members"]
    raw_id_fields = ("chairman", "second_chair", "cashier", "secretary")

    actions = ["export_csv_union_info"]

    def get_fieldsets(self, request, obj=None):
        # 20241113: https://stackoverflow.com/questions/16102222/djangoremove-superuser-checkbox-from-django-admin-panel-when-login-staff-users

        info_fields = [
            "bank_main_org",
            "bank_account",
            "statues",
            "founded_at",
            "closed_at",
            "memberships_allowed_at",
            "membership_price_in_dkk",
        ]

        if request.user.is_superuser or request.user.has_perm(
            "members.show_ledger_account"
        ):
            info_fields.append("gl_account")

        if request.user.is_superuser or request.user.has_perm(
            "members.show_new_membership_model"
        ):
            info_fields.append("new_membership_model_activated_at")

        return [
            (
                "Navn og Adresse",
                {
                    "fields": ("name", "cvr", "email", "address"),
                    "description": "<p>Udfyld navnet på foreningen (f.eks København, \
                        vestjylland) og adressen<p>",
                },
            ),
            (
                "Bestyrelsen nye felter",
                {
                    "fields": (
                        "chairman",
                        "second_chair",
                        "cashier",
                        "secretary",
                        "board_members",
                    )
                },
            ),
            (
                "Bestyrelsen gamle felter",
                {
                    "fields": (
                        "chairman_old",
                        "chairman_email_old",
                        "second_chair_old",
                        "second_chair_email_old",
                        "cashier_old",
                        "cashier_email_old",
                        "secretary_old",
                        "secretary_email_old",
                        "board_members_old",
                    )
                },
            ),
            (
                "Info",
                {
                    "fields": info_fields,
                    "description": "Indsæt et link til jeres vedtægter, hvornår I er stiftet (har holdt stiftende \
                    generalforsamling) og jeres bankkonto hvis I har sådan en til foreningen.",
                },
            ),
        ]

    def get_readonly_fields(self, request, obj=None):
        if obj and (
            (
                request.user.is_superuser
                or request.user.has_perm("members.show_new_membership_model")
            )
            and (
                obj.new_membership_model_activated_at is not None
                and obj.new_membership_model_activated_at <= now()
            )
        ):
            return [
                "new_membership_model_activated_at",
            ]
        return []

    # Solution found on https://stackoverflow.com/questions/57056994/django-model-form-with-only-view-permission-puts-all-fields-on-exclude
    # formfield_for_foreignkey described in documentation here: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.formfield_for_foreignkey
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "address":
            kwargs["queryset"] = Address.get_user_addresses(request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "board_members":
            kwargs["queryset"] = Person.objects.filter(user__is_staff=True).order_by(
                Upper("name")
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(UnionAdmin, self).get_queryset(request)
        qs = qs.annotate(waitinglist_count=Count("department__waitinglist"))
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_unions"
        ):
            return qs
        return qs.filter(adminuserinformation__user=request.user)

    def union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.id])
        link = '<a href="%s">%s</a>' % (url, escape(item.name))
        return mark_safe(link)

    union_link.short_description = "Forening"
    union_link.admin_order_field = "name"

    def waitinglist_count_link(self, item):
        waitinglist_count = 0
        for department in Department.objects.all().filter(union=item.id):
            waitinglist_count += department.waitinglist_set.count()
        admin_url = reverse("admin:members_waitinglist_changelist")
        link = f"""<a
            href="{admin_url}?={item.id}"
            title="Vis venteliste for forening Coding Pirates {item.name}">
            {waitinglist_count}
            </a>"""
        return mark_safe(link)

    waitinglist_count_link.short_description = "Venteliste"
    waitinglist_count_link.admin_order_field = "waitinglist_count"

    def export_csv_union_info(self, request, queryset):
        result_string = generate_union_csv(queryset)
        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("UTF-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="foreningsoversigt.csv"'
        return response

    export_csv_union_info.short_description = "Exporter Foreningsinformationer"

    def has_cvr_number(self, obj):
        return bool(obj.cvr and obj.cvr.strip())

    has_cvr_number.boolean = True
    has_cvr_number.short_description = "CVR"
    has_cvr_number.admin_order_field = "cvr"
