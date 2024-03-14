from django.contrib import admin

from .inlines import EquipmentLoanInline


class EquipmentAdmin(admin.ModelAdmin):
    list_filter = ["department", "union"]
    list_display = ["title", "count", "union", "department"]
    search_fields = ("title", "notes")
    raw_id_fields = ("department", "union")
    inlines = (EquipmentLoanInline,)
    list_per_page = 20
