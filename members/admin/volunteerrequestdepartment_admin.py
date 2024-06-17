from django.contrib import admin


class VolunteerRequestDepartmentAdmin(admin.ModelAdmin):
    list_display = ("volunteer_request", "department", "created", "finished", "status")

    date_hierarchy = "created"

    list_filter = ("department", "status")
