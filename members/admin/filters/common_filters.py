"""Admin list filters shared across multiple model admins."""

from django.contrib import admin


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
