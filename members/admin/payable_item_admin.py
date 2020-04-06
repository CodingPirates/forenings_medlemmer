from django.contrib import admin
from members.models import PayableItem


class PayableItemAdmin(admin.ModelAdmin):
    list_display = (
        "added",
        "person",
        "refunded",
        "quick_pay_id",
        "accepted",
        "amount_ore",
    )
    list_filter = ("refunded", "accepted")
    readonly_fields = [
        "added",
        "person",
        "refunded",
        "quick_pay_id",
        "accepted",
        "amount_ore",
    ]
    fieldsets = [
        ("Data", {"fields": ("person", "added", "amount_ore", "quick_pay_id")}),
        ("Status", {"fields": ("refunded", "accepted",)}),
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
