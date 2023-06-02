from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.conf import settings

from members.models import Address, AdminUserInformation, admin_user_information, person

# class UnionInline(admin.StackedInline):
#    model = AdminUserInformation
#    filter_horizontal = ("board_members", "user")
#    can_delete = False


class UnionAdmin(admin.ModelAdmin):
    # inlines = (UnionInline,)
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
    filter_horizontal = ["board_members", "adminuserinformation"]
    raw_id_fields = ("chairman", "second_chair", "cashier", "secretary")

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
            "Admins",
            {"fields": ("adminuserinformation",)},
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
