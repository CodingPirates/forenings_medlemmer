from django.conf import settings
from django.contrib import admin


class PaymentAdmin(admin.ModelAdmin):
    list_per_page = settings.LIST_PER_PAGE

    list_display = [
        "pk",
        "added_at",
        "payment_type",
        "amount_ore",
        "family",
        "confirmed_at",
        "cancelled_at",
        "rejected_at",
        "activityparticipant",
    ]
    list_filter = ["payment_type", "activity"]
    raw_id_fields = ("person", "activityparticipant", "family", "member")
    date_hierarchy = "added_at"
    search_fields = ("family__email",)
    select_related = "activityparticipant"
