from django.contrib import admin


class PaymentAdmin(admin.ModelAdmin):
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
    raw_id_fields = ("person", "activityparticipant", "family")
    date_hierarchy = "added_at"
    search_fields = ("family__email",)
    select_related = "activityparticipant"
