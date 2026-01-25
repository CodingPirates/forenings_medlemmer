import codecs
import csv
from io import StringIO
from django.http import HttpResponse
from django.conf import settings
from django.contrib import admin

from members.models import (
    Union,
)
from members.models.payment import Payment

from rangefilter.filters import (
    DateRangeFilterBuilder,
)

from .filters.member_admin_filters import (
    MemberCurrentYearListFilter,
    MemberLastYearListFilter,
    MemberAdminListFilter,
)


def generate_member_csv(member_queryset, include_address=False):
    """Generate a CSV string with member information from the given queryset. Optionally include address fields."""
    output = StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\n")

    header = [
        "Navn",
        "Køn",
        "Fødselsdato",
        "Email",
        "Forældre navn",
        "Forældre telefon",
        "Familie email",
        "Kommune",
        "Forening",
        "Medlem fra",
        "Medlem til",
        "Betalingsdato",
    ]
    if include_address:
        header += [
            "Adresse",
            "Postnr-by",
        ]
    writer.writerow(header)

    for member in member_queryset:
        gender = member.person.gender_text()
        birthdate = (
            member.person.birthday.strftime("%Y-%m-%d")
            if member.person.birthday
            else ""
        )
        parent = member.person.family.get_first_parent()
        if parent:
            parent_name = parent.name
            parent_phone = parent.phone
        else:
            parent_name = ""
            parent_phone = ""
        if not member.person.family.dont_send_mails:
            family_email = member.person.family.email
            email = member.person.email
        else:
            family_email = ""
            email = ""
        municipality = (
            member.person.municipality.name if member.person.municipality else ""
        )
        member_since = (
            member.member_since.strftime("%Y-%m-%d") if member.member_since else ""
        )
        member_until = (
            member.member_until.strftime("%Y-%m-%d") if member.member_until else ""
        )

        # Find betalingsdato (accepted_at) for medlemmet
        payment = None
        accepted_at = ""
        try:
            payment = (
                Payment.objects.filter(member=member, accepted_at__isnull=False)
                .order_by("-accepted_at")
                .first()
            )
            if payment and payment.accepted_at:
                accepted_at = payment.accepted_at.strftime("%Y-%m-%d")
        except Exception:
            accepted_at = ""

        row = [
            member.person.name,
            gender,
            birthdate,
            email,
            parent_name,
            family_email,
            parent_phone,
            municipality,
            member.union.name,
            member_since,
            member_until,
            accepted_at,
        ]
        if include_address:
            street = member.person.streetname or ""
            housenumber = member.person.housenumber or ""
            floor = member.person.floor or ""
            door = member.person.door or ""
            zipcode = member.person.zipcode or ""
            city = member.person.city or ""
            # Brug samme formattering som format_address
            address_str = street + " " + housenumber
            if floor and door:
                address_str += f", {floor}. {door}."
            elif floor:
                address_str += f", {floor}."
            elif door:
                address_str += f", {door}."
            zip_city_str = f"{zipcode} {city}".strip()
            row += [address_str, zip_city_str]
        writer.writerow(row)
    return output.getvalue()


class MemberAdmin(admin.ModelAdmin):
    search_fields = [
        "person__name",
        "person__email",
    ]
    list_per_page = settings.LIST_PER_PAGE
    date_hierarchy = "member_since"
    list_display = [
        "person",
        "union",
        "member_since",
        "member_until",
    ]

    list_filter = [
        "person__gender",
        MemberCurrentYearListFilter,
        MemberLastYearListFilter,
        MemberAdminListFilter,
        ("person__birthday", DateRangeFilterBuilder()),
    ]

    autocomplete_fields = ("union", "person")

    actions = ["export_csv_member_info", "export_csv_member_address"]

    def get_queryset(self, request):
        qs = super(MemberAdmin, self).get_queryset(request)
        if (
            request.user.is_superuser
            or request.user.has_perm("members.view_all_persons")
            or request.user.has_perm("members.view_all_unions")
        ):
            return qs
        else:
            unions = Union.objects.filter(
                adminuserinformation__user=request.user
            ).values("id")
            return qs.filter(union__in=unions)

    def export_csv_member_info(self, request, queryset):
        result_string = generate_member_csv(queryset, include_address=False)
        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("UTF-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="medlemsoversigt.csv"'
        return response

    export_csv_member_info.short_description = "Eksporter medlemsinformation (CSV)"

    def export_csv_member_address(self, request, queryset):
        # Sikkerhedstjek: kun superuser eller brugere med 'members.export_address' permission
        if not (
            request.user.is_superuser or request.user.has_perm("members.export_address")
        ):
            self.message_user(
                request, "Du har ikke adgang til at eksportere adresser.", level="error"
            )
            return None
        result_string = generate_member_csv(queryset, include_address=True)
        response = HttpResponse(
            f'{codecs.BOM_UTF8.decode("UTF-8")}{result_string}',
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="medlemsadresser.csv"'
        return response

    export_csv_member_address.short_description = (
        "Eksporter medlemsinformation med adresser (CSV)"
    )
