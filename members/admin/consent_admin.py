from django.conf import settings
from django.contrib import admin
from django.db.models.deletion import ProtectedError
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from members.models import Person


class ConsentAdmin(admin.ModelAdmin):
    list_per_page = 50
    change_form_template = "admin/members/consent/change_form.html"

    list_display = (
        "id",
        "released_at",
        "title",
        "active",
        "preview_link",
    )
    list_filter = ("released_at",)
    search_fields = ("consent_text",)
    readonly_fields = ("preview_link",)

    def active(self, item):
        return item.is_active()

    active.short_description = "Aktiv"
    active.boolean = True
    active.admin_order_field = "is_active"

    def preview_link(self, obj):
        if obj.id is None:
            return ""

        full_url = f"{settings.BASE_URL}{reverse('consent_preview', args=[obj.id])}"
        link = format_html(
            '<a href="{}" target="_blank">{}</a> ',
            full_url,
            full_url,
        )

        return mark_safe(link)

    preview_link.short_description = "Preview"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and Person.objects.filter(consent_id=obj.id).exists():
            readonly_fields += [field.name for field in self.model._meta.fields]
            readonly_fields += ["preview_link"]
        return tuple(readonly_fields)

    def save_model(self, request, obj, form, change):
        if change:  # If the object is being changed
            if Person.objects.filter(consent_id=obj.id).exists():
                self.message_user(
                    request,
                    "This consent record is used by a person record and cannot be changed.",
                    level=messages.ERROR,
                )
                return
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ProtectedError:
            self.message_user(
                request,
                "This consent record is used by a person record and cannot be deleted.",
                level=messages.ERROR,
            )

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and Person.objects.filter(consent_id=obj.id).exists():
            extra_context = extra_context or {}
            extra_context["readonly"] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "released_at",
                    "title",
                    "text",
                    "preview_link",
                )
            },
        ),
    )
