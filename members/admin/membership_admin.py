from django.contrib import admin


class MembershipAdmin(admin.ModelAdmin):
    list_display = ("person", "union", "sign_up_date")
    list_filter = ("union", "sign_up_date", "sign_up_date")
    readonly_fields = ["person", "union", "sign_up_date"]
    fieldsets = [
        ("Medlemskab", {"fields": ("person", "union", "sign_up_date")}),
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
