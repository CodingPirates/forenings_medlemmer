from django.conf import settings
from django.contrib import admin

from .inlines import EquipmentLoanInline


class EquipmentAdmin(admin.ModelAdmin):
    list_per_page = settings.LIST_PER_PAGE

    list_filter = ["department", "union"]
    list_display = ["title", "count", "union", "department"]
    search_fields = ("title", "notes")
    autocomplete_fields = ("department", "union")
    inlines = (EquipmentLoanInline,)
