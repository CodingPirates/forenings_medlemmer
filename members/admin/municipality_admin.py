from django.conf import settings
from django.contrib import admin


class MunicipalityAdmin(admin.ModelAdmin):
    list_per_page = settings.LIST_PER_PAGE
    list_display = ("key_column", "name", "address", "zipcode", "city", "dawa_id")
    search_fields = ("name", "address", "zipcode", "city")

    @admin.display(ordering="pk", description="key")
    def key_column(self, obj):
        return obj.pk
