from django.contrib import admin
from django.utils import timezone

from members.models import AdminUserInformation, Union


class MemberCurrentYearListFilter(admin.SimpleListFilter):
    title = "Medlem i år " + str(timezone.now().year)
    parameter_name = "member_list_current_year"

    def lookups(self, request, _model_admin):
        unions = [("none", "Ikke medlem"), ("any", "Alle medlemmer samlet")]
        for union in Union.objects.filter(
            pk__in=AdminUserInformation.get_unions_admin(request.user)
        ).order_by("name"):
            unions.append((str(union.pk), str(union)))

        if len(unions) <= 1:
            return ()

        return unions

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(union__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(union__isnull=True).filter(
                member_since__year=timezone.now().year
            )
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(union=self.value()).filter(
                member_since__year=timezone.now().year
            )


class MemberLastYearListFilter(admin.SimpleListFilter):
    title = "Medlem i år " + str(timezone.now().year - 1)
    parameter_name = "member_list_last_year"

    def lookups(self, request, _model_admin):
        unions = [("none", "Ikke medlem"), ("any", "Alle medlemmer samlet")]
        for union in Union.objects.filter(
            pk__in=AdminUserInformation.get_unions_admin(request.user)
        ).order_by("name"):
            unions.append((str(union.pk), str(union)))

        if len(unions) <= 1:
            return ()

        return unions

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(union__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(union__isnull=True).filter(
                member_since__year=timezone.now().year - 1
            )
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(union=self.value()).filter(
                member_since__year=timezone.now().year - 1
            )


class MemberAdminListFilter(admin.SimpleListFilter):
    title = "Medlem"
    parameter_name = "member_list"

    def lookups(self, request, _model_admin):
        unions = [("none", "Ikke medlem"), ("any", "Alle medlemmer samlet")]
        for union in Union.objects.filter(
            pk__in=AdminUserInformation.get_unions_admin(request.user)
        ).order_by("name"):
            unions.append((str(union.pk), str(union)))

        if len(unions) <= 1:
            return ()

        return unions

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(union__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(union__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(union=self.value())
