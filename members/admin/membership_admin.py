from django.contrib import admin


class MembershipAdmin(admin.ModelAdmin):
    list_display = ("person", "union", "sign_up_date")
    list_filter = ("union", "sign_up_date")
    fieldsets = [
        ("Medlemskab", {"fields": ("person", "union", "sign_up_date")}),
    ]
