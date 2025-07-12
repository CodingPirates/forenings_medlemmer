from django.conf import settings
from django.contrib import admin

from members.models import (
    Union,
)

from rangefilter.filters import (
    DateRangeFilterBuilder,
)

from .filters.member_admin_filters import (
    MemberCurrentYearListFilter,
    MemberLastYearListFilter,
    MemberAdminListFilter,
)


class MemberAdmin(admin.ModelAdmin):
    list_per_page = settings.LIST_PER_PAGE

    list_display = [
        "person",
        "union",
        "member_since",
        "member_until",
    ]

    list_filter = [
        "person__gender",
        MemberCurrentYearListFilter,
        MemberLastYearListFilter,
        MemberAdminListFilter,
        ("person__birthday", DateRangeFilterBuilder()),
    ]

    raw_id_fields = [
        "union",
        "person",
    ]

    def get_queryset(self, request):
        qs = super(MemberAdmin, self).get_queryset(request)
        if (
            request.user.is_superuser
            or request.user.has_perm("members.view_all_persons")
            or request.user.has_perm("members.view_all_unions")
        ):
            return qs
        else:
            unions = Union.objects.filter(
                adminuserinformation__user=request.user
            ).values("id")
            return qs.filter(union__in=unions)
