from decimal import Decimal

from django.utils import timezone
from django.utils.formats import number_format
from django.utils.html import format_html

from django.conf import settings
from django.contrib import admin
import pytz


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
        "id",
        "get_added_at_display",
        "payment_type",
        "get_payment_amount",
        "get_family_email",
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
        return self.utc_to_local_ymdhms(obj.added_at) if obj.added_at else ""

    get_added_at_display.short_description = "Tilføjet"

    def get_confirmed_at_display(self, obj):
        return self.utc_to_local_ymdhms(obj.confirmed_at) if obj.confirmed_at else ""

    get_confirmed_at_display.short_description = "Bekræftet"

    def get_accepted_at_display(self, obj):
        return self.utc_to_local_ymdhms(obj.accepted_at) if obj.accepted_at else ""

    get_accepted_at_display.short_description = "Accepteret"

    def get_cancelled_at_display(self, obj):
        return self.utc_to_local_ymdhms(obj.cancelled_at) if obj.cancelled_at else ""

    get_cancelled_at_display.short_description = "Annulleret"

    def get_rejected_at_display(self, obj):
        return self.utc_to_local_ymdhms(obj.rejected_at) if obj.rejected_at else ""

    get_rejected_at_display.short_description = "Afvist"

    def get_activityparticipant_display(self, obj):
        return obj.activityparticipant

    get_activityparticipant_display.short_description = "Aktivitetsdeltager"

    def get_family_email(self, obj):
        return obj.family.email

    get_family_email.short_description = "Familie email"

    @admin.display(description="Beløb (DKK)", ordering="amount_ore")
    def get_payment_amount(self, obj):
        amount_dkk = Decimal(obj.amount_ore) / Decimal("100")
        formatted_amount = number_format(amount_dkk, decimal_pos=2, use_l10n=True)
        return format_html(
            '<span class="payment-amount">{}</span>',
            formatted_amount,
        )

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

    @staticmethod
    def utc_to_local_ymdhms(timestamp_utc):
        ymdhms = "%Y-%m-%d %H:%M:%S"
        utc = timestamp_utc.replace(tzinfo=pytz.UTC)
        local_time = utc.astimezone(timezone.get_current_timezone())
        return local_time.strftime(ymdhms)
