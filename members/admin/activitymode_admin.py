from django.contrib import admin
from members.models.activitymode import ActivityMode


@admin.register(ActivityMode)
class ActivityModeAdmin(admin.ModelAdmin):
    list_display = ("key_column", "code", "name", "description")
    search_fields = ("code", "name", "description")

    @admin.display(ordering="pk", description="key")
    def key_column(self, obj):
        return obj.pk
