from django.contrib import admin


class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ("municipality", "address", "zipcode", "city", "email")
