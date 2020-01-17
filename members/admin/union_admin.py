from django.contrib import admin

from members.models import Address


class UnionAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(UnionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["address"].queryset = Address.get_user_addresses(request.user)
        return form

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
            "Bestyrelsen",
            {
                "fields": (
                    "chairman",
                    "chairman_email",
                    "second_chair",
                    "second_chair_email",
                    "cashier",
                    "cashier_email",
                    "secretary",
                    "secratary_email",
                    "boardMembers",
                )
            },
        ),
        (
            "Info",
            {
                "fields": ("bank_main_org", "bank_account", "statues", "founded"),
                "description": "Indsæt et link til jeres vedtægter, hvornår I er stiftet (har holdt stiftende \
                generalforsamling) og jeres bankkonto hvis I har sådan en til foreningen.",
            },
        ),
    ]

    list_display = ("name", "address")
