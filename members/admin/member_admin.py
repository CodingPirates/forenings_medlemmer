from glob import escape
import codecs
import csv
from io import StringIO
from django.http import HttpResponse
from django.conf import settings
from django.contrib import admin
from django.db.models import Case, OuterRef, Subquery, When
from django.urls import reverse
from django.utils.safestring import mark_safe

from members.models import (
    Union,
)
from members.models.payment import Payment

from rangefilter.filters import (
    DateRangeFilterBuilder,
)

from .admin_actions import AdminActions, MemberSummaryExportMixin
from .filters.member_admin_filters import (
    MemberCurrentYearListFilter,
    MemberLastYearListFilter,
    MemberAdminListFilter,
    MemberPaymentListFilter,
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
        "Familie email",
        "Forældre telefon",
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
        member_since = member.member_since.strftime("%Y-%m-%d")
        member_until = member.member_until.strftime("%Y-%m-%d")

        payment = (
            Payment.objects.filter(member=member, confirmed_at__isnull=False)
            .order_by("-confirmed_at")
            .first()
        )
        confirmed_at = (
            payment.confirmed_at.strftime("%Y-%m-%d")
            if payment
            and payment.confirmed_at
            and payment.cancelled_at is None
            and payment.refunded_at is None
            and payment.rejected_at is None
            else ""
        )

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
            confirmed_at,
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


class MemberAdmin(MemberSummaryExportMixin, admin.ModelAdmin):
    search_fields = [
        "person__name",
        "person__email",
    ]
    list_per_page = settings.LIST_PER_PAGE
    date_hierarchy = "member_since"
    list_display = [
        "id",
        "person_link",
        "union_link",
        "member_since",
        "member_until",
        "confirmed_at",
    ]

    list_filter = [
        "person__gender",
        MemberPaymentListFilter,
        MemberCurrentYearListFilter,
        MemberLastYearListFilter,
        MemberAdminListFilter,
        ("person__birthday", DateRangeFilterBuilder()),
    ]

    autocomplete_fields = ("union", "person")

    actions = [
        "export_csv_member_summary",
        "export_csv_member_info",
        "export_csv_member_address",
        AdminActions.create_volunteer_action,
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Tilføj kun export_csv_member_address hvis brugeren har rettigheden eller er superuser
        if request.user.is_superuser or request.user.has_perm(
            "members.member_export_address"
        ):
            actions["export_csv_member_address"] = (
                MemberAdmin.export_csv_member_address,
                "export_csv_member_address",
                MemberAdmin.export_csv_member_address.short_description,
            )
        else:
            # Hvis den er der (f.eks. fra arvet konfiguration), fjern den
            actions.pop("export_csv_member_address", None)
        return actions

    def get_queryset(self, request):
        latest_payment = Payment.objects.filter(
            member=OuterRef("pk"), confirmed_at__isnull=False
        ).order_by("-confirmed_at")
        qs = (
            super(MemberAdmin, self)
            .get_queryset(request)
            .annotate(
                latest_payment_confirmed_at=Subquery(
                    latest_payment.annotate(
                        latest_payment_confirmed_at=Case(
                            When(
                                cancelled_at__isnull=True,
                                refunded_at__isnull=True,
                                rejected_at__isnull=True,
                                then="confirmed_at",
                            )
                        )
                    ).values("latest_payment_confirmed_at")[:1]
                )
            )
        )
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

    @admin.display(description="Betalingsdato", ordering="latest_payment_confirmed_at")
    def confirmed_at(self, item):
        if item.latest_payment_confirmed_at:
            return item.latest_payment_confirmed_at.strftime("%Y-%m-%d")
        return ""

    def person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.person_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.person.name))
        return mark_safe(link)

    person_link.short_description = "Person"
    person_link.admin_order_field = "person__name"

    def union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.union_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.union.name))
        return mark_safe(link)

    union_link.short_description = "Forening"
    union_link.admin_order_field = "union__name"

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
            request.user.is_superuser
            or request.user.has_perm("members.member_export_address")
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

    fieldsets = [
        (None, {"fields": ["person", "union", "member_since", "member_until"]}),
    ]
