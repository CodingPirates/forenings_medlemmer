from django.contrib import admin
from members.models import Address


class AddressAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created_at",
        "created_by",
    )

    def get_queryset(self, request):
        return Address.get_user_addresses(request.user)

    fieldsets = [
        (
            "Adresse",
            {
                "fields": (
                    "streetname",
                    "housenumber",
                    "floor",
                    "door",
                    "zipcode",
                    "city",
                    "municipality",
                    "region",
                )
            },
        ),
        (
            "Dawa info",
            {
                "fields": ("dawa_id", "dawa_overwrite", "longitude", "latitude"),
                "classes": ("collapse",),
            },
        ),
        (
            "Yderlige data",
            {
                "fields": ("created_at", "created_by"),
                "description": "Hvornår er denne adresse oprettet og af hvem ?",
                "classes": ("collapse",),
            },
        ),
    ]
