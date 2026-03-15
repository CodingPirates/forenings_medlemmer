from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.safestring import mark_safe

from members.models.slackinvitelog import SlackInviteLog


class CreatedBySlackLogFilter(admin.SimpleListFilter):
    title = "created by"
    parameter_name = "created_by"

    def lookups(self, request, model_admin):
        User = get_user_model()
        user_ids = SlackInviteLog.objects.values_list(
            "created_by", flat=True
        ).distinct()
        users = User.objects.filter(id__in=user_ids)
        return [(u.id, str(u)) for u in users if u]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created_by_id=self.value())
        return queryset


class SlackInviteLogAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "created_at",
                    "email_multiline",
                    "purpose",
                    "invite_url",
                    "created_by",
                    "status",
                    "message",
                ),
                "description": "Log for Slack invitation og evt. fejl.",
            },
        ),
        (
            "Løsningsstatus",
            {
                "fields": ("resolved_at", "resolved_by", "resolution_note"),
                "description": "Dokumentér hvem der håndterede fejlen og hvornår.",
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        ro = list(self.readonly_fields)
        ro += ["resolved_by", "resolved_at"]
        return ro

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        if obj.status == 6 and ("status" in form.changed_data or not change):
            obj.resolved_by = request.user
            obj.resolved_at = timezone.now()

        super().save_model(request, obj, form, change)

    def formatted_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if obj.created_at else ""

    formatted_created_at.admin_order_field = "created_at"
    formatted_created_at.short_description = "Oprettet"

    def email_summary(self, obj):
        return obj.email_summary()

    email_summary.short_description = "Email(s)"

    list_display = (
        "id",
        "formatted_created_at",
        "email_summary",
        "created_by",
        "status",
    )
    list_filter = ("status", CreatedBySlackLogFilter)
    search_fields = ("emails", "message")
    readonly_fields = (
        "id",
        "created_at",
        "email_multiline",
        "purpose",
        "invite_url",
        "created_by",
        "message",
    )

    def email_multiline(self, obj):
        emails = obj.emails.split()
        return mark_safe("<br>".join(emails))

    email_multiline.short_description = "Email(s)"

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        # Remove 'email' if present, only show 'email_multiline'
        if "email" in fields:
            fields.remove("email")
        # Ensure 'email_multiline' is present and after 'created_at'
        if "email_multiline" not in fields:
            insert_at = 1 if "created_at" in fields else 0
            fields.insert(insert_at, "email_multiline")
        # Move 'created_at' to the top
        if "created_at" in fields:
            fields.insert(0, fields.pop(fields.index("created_at")))
        return fields

    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if obj.created_at else ""

    created_at_display.short_description = "Created at"
