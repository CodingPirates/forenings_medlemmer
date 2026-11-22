from glob import escape
import codecs
import csv
from datetime import date
from io import StringIO
from django import forms
from django.http import HttpResponse
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.validators import MinValueValidator
from django.db.models import Count, Exists, OuterRef, Q, Subquery
from django.shortcuts import render
from django.urls import reverse
from django.utils import formats
from django.utils.safestring import mark_safe

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
            if payment and payment.confirmed_at
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


MEMBER_SUMMARY_MIN_DATE = date(2026, 1, 1)


class MemberSummaryExportForm(forms.Form):
    date = forms.DateField(
        label="Dato",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        minimum_date = formats.date_format(MEMBER_SUMMARY_MIN_DATE, "j. F Y")
        message = f"Datoen skal være {minimum_date} eller senere."
        self.fields["date"].widget.attrs["min"] = MEMBER_SUMMARY_MIN_DATE.isoformat()
        self.fields["date"].help_text = message
        self.fields["date"].validators.append(
            MinValueValidator(MEMBER_SUMMARY_MIN_DATE, message=message)
        )


class MemberAdmin(admin.ModelAdmin):
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
                    latest_payment.values("confirmed_at")[:1]
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

    def has_export_member_summary_permission(self, request):
        return request.user.has_perm("members.member_export_summary")

    @admin.action(
        permissions=["export_member_summary"],
        description="Eksporter medlemsoversigt pr. forening (CSV)",
    )
    def export_csv_member_summary(self, request, queryset):
        if not self.has_export_member_summary_permission(request):
            raise PermissionDenied
        form = MemberSummaryExportForm(
            request.POST if "export_summary" in request.POST else None
        )
        if form.is_bound and form.is_valid():
            date = form.cleaned_data["date"]
            paid_by_date = Payment.objects.filter(
                member=OuterRef("pk"), confirmed_at__date__lte=date
            )
            summary = (
                queryset.filter(member_since__lte=date, member_until__gte=date)
                .annotate(paid_by_date=Exists(paid_by_date))
                .order_by()
                .values("union_id", "union__name")
                .annotate(
                    paid=Count("pk", filter=Q(paid_by_date=True), distinct=True),
                    unpaid=Count("pk", filter=Q(paid_by_date=False), distinct=True),
                )
                .order_by("union__name", "union_id")
            )
            response = HttpResponse(content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = (
                f'attachment; filename="medlemsoversigt-{date.isoformat()}.csv"'
            )
            response.write(codecs.BOM_UTF8.decode("UTF-8"))
            writer = csv.writer(response, delimiter=";", lineterminator="\n")
            writer.writerow(
                [
                    "Forening",
                    "Betalt senest " + date.isoformat(),
                    "Betalt senere eller ikke betalt",
                ]
            )
            for row in summary:
                writer.writerow([row["union__name"], row["paid"], row["unpaid"]])
            return response

        context = {
            **self.admin_site.each_context(request),
            "title": "Eksporter medlemsoversigt pr. forening",
            "form": form,
            "queryset": queryset,
            "opts": self.model._meta,
        }
        return render(request, "admin/member_summary_export.html", context)

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
