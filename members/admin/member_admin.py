from glob import escape
from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

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
    search_fields = [
        "person__name",
        "person__email",
    ]
    list_per_page = settings.LIST_PER_PAGE
    date_hierarchy = "member_since"
    list_display = [
        "id",
        "person_link",
        "union_link",
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

    def person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.person_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.person.name))
        return mark_safe(link)

    person_link.short_description = "Person"
    person_link.admin_order_field = "person__name"

    def union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.union_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.union.name))
        return mark_safe(link)

    union_link.short_description = "Forening"
    union_link.admin_order_field = "union__name"
