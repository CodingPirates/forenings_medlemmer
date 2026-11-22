"""Admin list filters shared across multiple model admins."""

from django.contrib import admin
from django.db.models import Max, OuterRef, Subquery
from django.utils import timezone

from members.models import Consent, Family


class AnonymizedFilter(admin.SimpleListFilter):
    title = "Anonymiseret"
    parameter_name = "anonymized"

    def lookups(self, request, model_admin):
        return [("yes", "Anonymiseret"), ("no", "Ikke anonymiseret")]

    def value(self):
        v = super().value()
        if v is None:
            return "no"
        return v

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(anonymized=True)
        return queryset.filter(anonymized=False)


class FamilyConsentFilter(admin.SimpleListFilter):
    """Filter by the family's latest consent id (see Family.get_consent_id).

    Subclasses set family_lookup to the path from the filtered model to its
    family, e.g. "person__family". For Family itself it is "pk".
    """

    title = "Privatlivspolitik"
    parameter_name = "family_consent"
    family_lookup = "pk"

    @staticmethod
    def _can_view(request):
        return request.user.is_superuser or request.user.has_perm(
            "members.view_consent_information"
        )

    def lookups(self, request, model_admin):
        if not self._can_view(request):
            return []
        return [("none", "Ingen")] + self._consent_choices()

    @staticmethod
    def _consent_choices():
        """Released consents labelled with the time they became active (drafts skipped)."""
        consents = list(
            Consent.objects.filter(released_at__isnull=False).order_by("released_at")
        )

        def fmt(dt):
            return timezone.localtime(dt).strftime("%Y-%m-%d %H:%M:%S")

        return [(str(c.id), f"{c.id} ({fmt(c.released_at)})") for c in consents]

    def queryset(self, request, queryset):
        value = self.value()
        if value is None or not self._can_view(request):
            return queryset
        latest = Subquery(
            Family.objects.filter(pk=OuterRef(self.family_lookup))
            .annotate(latest_consent=Max("person__consent_id"))
            .values("latest_consent")[:1]
        )
        queryset = queryset.annotate(family_consent_id_value=latest)
        if value == "none":
            return queryset.filter(family_consent_id_value__isnull=True)
        return queryset.filter(family_consent_id_value=value)


class PersonFamilyConsentFilter(FamilyConsentFilter):
    family_lookup = "person__family"
