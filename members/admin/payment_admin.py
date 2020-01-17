from django.contrib import admin


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "added",
        "payment_type",
        "amount_ore",
        "family",
        "confirmed_dtm",
        "cancelled_dtm",
        "rejected_dtm",
        "activityparticipant",
    ]
    list_filter = ["payment_type", "activity"]
    raw_id_fields = ("person", "activityparticipant", "family")
    date_hierarchy = "added"
    search_fields = ("family__email",)
    select_related = "activityparticipant"
