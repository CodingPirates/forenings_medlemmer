from django.contrib import admin
from members.models.activitymode import ActivityMode


@admin.register(ActivityMode)
class ActivityModeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "description")
    search_fields = ("code", "name", "description")
