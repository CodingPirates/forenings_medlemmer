from django.contrib import admin

from members.models.slacklog import SlackLog


@admin.register(SlackLog)
class SlackLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "slack_user_id", "slack_email", "action")
    search_fields = ("slack_user_id", "slack_email", "user__username", "action")
    list_filter = ("action", "timestamp")
    readonly_fields = ("timestamp",)
