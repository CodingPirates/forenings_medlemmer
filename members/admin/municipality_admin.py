from django.contrib import admin


class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "zipcode", "city", "dawa_id")
    search_fields = ("name", "address", "zipcode", "city")
