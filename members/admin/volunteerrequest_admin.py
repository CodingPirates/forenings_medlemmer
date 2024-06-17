from django.contrib import admin


class VolunteerRequestAdmin(admin.ModelAdmin):
    list_display = (
        "person",
        "name",
        "age",
        "email",
        "phone",
        "created",
        "finished",
        "token",
    )

    date_hierarchy = "created"
