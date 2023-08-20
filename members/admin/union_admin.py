import codecs
from django.contrib import admin
from django.db.models.functions import Upper
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from members.models import Address, Person


class UnionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "union_link",
        "address",
        "union_email",
        "founded_at",
        "closed_at",
    )
    list_filter = (
        "address__region",
        "founded_at",
        "closed_at",
    )
    filter_horizontal = ["board_members"]
    raw_id_fields = ("chairman", "second_chair", "cashier", "secretary")

    actions = ["export_csv_union_info"]

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
        if request.user.is_superuser:
            return qs
        return qs.filter(adminuserinformation__user=request.user)

    fieldsets = [
        (
            "Navn og Adresse",
            {
                "fields": ("name", "union_email", "address"),
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
                "fields": (
                    "bank_main_org",
                    "bank_account",
                    "statues",
                    "membership_price_in_dkk",
                    "founded_at",
                    "closed_at",
                ),
                "description": "Indsæt et link til jeres vedtægter, hvornår I er stiftet (har holdt stiftende \
                generalforsamling) og jeres bankkonto hvis I har sådan en til foreningen.",
            },
        ),
    ]

    def union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.id])
        link = '<a href="%s">%s</a>' % (url, item.name)
        return mark_safe(link)

    union_link.short_description = "Forening"
    union_link.admin_order_field = "name"

    def export_csv_union_info(self, request, queryset):
        result_string = "Forening;Oprettelsdato;Lukkedato;"
        result_string += "formand-navn;formand-email;formand-tlf;"
        result_string += "næstformand-navn;næstformand-email;næstformand-tlf;"
        result_string += "kasserer-navn;kasserer-email;kasserer-tlf;"
        result_string += "sekretær-navn;sekretær-email;sekretær-tlf\n"

        for union in queryset:
            result_string += union.name
            result_string += ";"
            if union.founded_at is not None:
                result_string += union.founded_at.strftime("%Y-%m-%d")
            result_string += ";"
            if union.closed_at is not None:
                result_string += union.closed_at.strftime("%Y-%m-%d")
            if union.chairman is None:
                result_string += ";;;"
            else:
                result_string += (
                    f";{union.chairman.name}"
                    f";{union.chairman.email}"
                    f";{union.chairman.phone}"
                )
            if union.second_chair is None:
                result_string += ";;;"
            else:
                result_string += (
                    f";{union.second_chair.name}"
                    f";{union.second_chair.email}"
                    f";{union.second_chair.phone}"
                )
            if union.cashier is None:
                result_string += ";;;"
            else:
                result_string += (
                    f";{union.cashier.name}"
                    f";{union.cashier.email}"
                    f";{union.cashier.phone}"
                )
            if union.secretary is None:
                result_string += ";;;"
            else:
                result_string += (
                    f";{union.secretary.name}"
                    f";{union.secretary.email}"
                    f";{union.secretary.phone}"
                )

            result_string += "\n"

        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("UTF-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="foreningsoversigt.csv"'
        return response

    export_csv_union_info.short_description = "Exporter Foreningsinformationer"
