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
        "get_added_at_display",
        "payment_type",
        "amount_ore",
        "family",
        "get_confirmed_at_display",
        "get_accepted_at_display",
        "get_cancelled_at_display",
        "get_rejected_at_display",
        "get_activityparticipant_display",
        "get_member_display",
    ]

    readonly_fields = ["pk"]
    list_filter = [
        "payment_type",
        "activity",
    ]

    def get_added_at_display(self, obj):
        return obj.added_at.strftime("%Y-%m-%d %H:%M") if obj.added_at else ""

    get_added_at_display.short_description = "Tilføjet"

    def get_confirmed_at_display(self, obj):
        return obj.confirmed_at.strftime("%Y-%m-%d %H:%M") if obj.confirmed_at else ""

    get_confirmed_at_display.short_description = "Bekræftet"

    def get_accepted_at_display(self, obj):
        return obj.accepted_at.strftime("%Y-%m-%d %H:%M") if obj.accepted_at else ""

    get_accepted_at_display.short_description = "Accepteret"

    def get_cancelled_at_display(self, obj):
        return obj.cancelled_at.strftime("%Y-%m-%d %H:%M") if obj.cancelled_at else ""

    get_cancelled_at_display.short_description = "Annulleret"

    def get_rejected_at_display(self, obj):
        return obj.rejected_at.strftime("%Y-%m-%d %H:%M") if obj.rejected_at else ""

    get_rejected_at_display.short_description = "Afvist"

    def get_activityparticipant_display(self, obj):
        return obj.activityparticipant

    get_activityparticipant_display.short_description = "Aktivitetsdeltager"

    def get_member_display(self, obj):
        return obj.member

    get_member_display.short_description = "medlemskab"
    list_filter = ["payment_type", "activity"]
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
