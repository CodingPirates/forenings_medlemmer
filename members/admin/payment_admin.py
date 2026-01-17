from django.conf import settings
from django.contrib import admin


class PaymentAdmin(admin.ModelAdmin):
    fields = [
        "pk",
        "added_at",
        "payment_type",
        "activityparticipant",
        "activity",
        "member",
        "family",
        "person",
        "amount_ore",
        "body_text",
        "accepted_at",
        "confirmed_at",
        "cancelled_at",
        "refunded_at",
        "rejected_at",
        "rejected_message",
        "reminder_sent_at",
    ]
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

    readonly_fields = ["pk"]
    list_filter = [
        "payment_type",
        "activity",
    ]
    # raw_id_fields = ("person", "family", "member")
    date_hierarchy = "added_at"
    search_fields = ("family__email",)
    select_related = "activityparticipant"
    autocomplete_fields = (
        "activity",
        "activityparticipant",
        "member",
        "person",
        "family",
    )

    class Media:
        css = {"all": ("members/css/custom_admin.css",)}
