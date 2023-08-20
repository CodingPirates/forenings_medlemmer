from django.contrib import admin
from members.models import Member


class MemberAdmin(admin.ModelAdmin):
    list_display = [
        "person",
        "union",
        "member_since",
        "member_until",
    ]

    raw_id_fields = [
        "union",
        "person",
    ]
