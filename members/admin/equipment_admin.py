from django.conf import settings
from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.urls import reverse
from .inlines import EquipmentLoanInline


class EquipmentAdmin(admin.ModelAdmin):
    list_per_page = settings.LIST_PER_PAGE

    list_filter = ["department", "union"]
    list_display = ["key_column", "title", "count", "union_link", "department_link"]
    search_fields = ("title", "notes")
    raw_id_fields = ("department", "union")
    inlines = (EquipmentLoanInline,)

    @admin.display(ordering="pk", description="key")
    def key_column(self, obj):
        return obj.pk

    def union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.union_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.union.name))
        return mark_safe(link)

    union_link.short_description = "Forening"
    union_link.admin_order_field = "union__name"

    def department_link(self, item):
        url = reverse("admin:members_department_change", args=[item.department_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.department.name))
        return mark_safe(link)

    department_link.short_description = "Afdeling"
    department_link.admin_order_field = "department__name"
