from django.contrib import admin
from django.utils import timezone

from members.models import AdminUserInformation, Union


class MemberPaymentListFilter(admin.SimpleListFilter):
    title = "Betalt"
    parameter_name = "payment_status"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Ja"),
            ("no", "Nej"),
            ("all", "Alle"),
        )

    def choices(self, changelist):
        value = self.value() or "yes"
        for lookup, title in self.lookup_choices:
            yield {
                "selected": value == lookup,
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        if self.value() in (None, "yes"):
            return queryset.filter(latest_payment_confirmed_at__isnull=False)
        if self.value() == "no":
            return queryset.filter(latest_payment_confirmed_at__isnull=True)
        return queryset


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
