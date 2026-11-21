from django.contrib import admin


class AuthLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "event",
        "success",
        "method",
        "identifier",
        "ip_address",
    )
    list_filter = ("event", "success", "method", "created_at")
    search_fields = ("identifier", "ip_address")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
