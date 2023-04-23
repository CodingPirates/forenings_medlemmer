from django import forms
from django.contrib import admin
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.html import escape

from members.models import (
    Activity,
    ActivityInvite,
    AdminUserInformation,
    Department,
    Union,
    Person,
)


class ActivityInviteAdminForm(forms.ModelForm):
    class Meta:
        model = ActivityInvite
        exclude = []

    def __init__(self, *args, **kwds):
        super(ActivityInviteAdminForm, self).__init__(*args, **kwds)
        self.fields["person"].queryset = Person.objects.order_by(Lower("name"))


class ActivivtyInviteActivityListFilter(admin.SimpleListFilter):
    title = "Aktiviteter"
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for activity in (
            Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user)
            )
            .order_by("department__name")
            .distinct()
        ):
            activitys.append((str(activity.pk), activity))

        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__pk=self.value())


class ActivityInviteUnionListFilter(admin.SimpleListFilter):
    title = "Lokalforeninger"
    parameter_name = "activity__department__union"

    def lookups(self, request, model_admin):
        unions = []
        for union in AdminUserInformation.get_unions_admin(request.user).order_by(
            "name"
        ):
            unions.append((str(union.pk), union.name))

        return unions

    def queryset(self, request, queryset):
        if self.value() == "any":
            return queryset.exclude(activity__department__union__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__department__union__pk=self.value())


class ActivityInviteDepartmentListFilter(admin.SimpleListFilter):
    title = "Afdelinger"
    parameter_name = "activity__department"

    def lookups(self, request, model_admin):
        departments = []
        for department in AdminUserInformation.get_departments_admin(request.user).order_by(
            "name"
        ):
            departments.append((str(department.pk), department.name))
        return departments

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity__department__pk=self.value())


class ActivitInviteListCurrentFilter(admin.SimpleListFilter):
    title = "Nuværende og kommende aktiviteter"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for act in (
            Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user),
                end_date__gte=timezone.now(),
            )
            .order_by("department__name", "-start_date")
            .distinct()
        ):
            activitys.append((str(act.pk), str(act)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity=self.value())


class ActivitInviteListFinishedFilter(admin.SimpleListFilter):
    title = "Tidligere aktiviteter"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        activitys = []
        for act in (
            Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user),
                end_date__lte=timezone.now(),
            )
            .order_by("department__name", "-start_date")
            .distinct()
        ):
            activitys.append((str(act.pk), str(act)))
        return activitys

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activity=self.value())


class ActivityInviteAdmin(admin.ModelAdmin):
    list_display = (
        "activity_department_union_link",
        "activity_department_link",
        "activity_link",
        "person_link",
        "invite_dtm",
        "expire_dtm",
        "person_age_years",
        "person_zipcode",
        "rejected_at",
    )
    list_filter = (
        ActivityInviteUnionListFilter,
        ActivityInviteDepartmentListFilter,
        # ActivivtyInviteActivityListFilter,
        ActivitInviteListCurrentFilter,
        ActivitInviteListFinishedFilter,
    )
    date_hierarchy = "activity__start_date"
    search_fields = (
        "activity__department__union__name",
        "activity__department__name",
        "activity__name",
        "person__name",
    )
    list_display_links = None
    form = ActivityInviteAdminForm

    # Only show invitation to own activities
    def get_queryset(self, request):
        qs = super(ActivityInviteAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(activity__department__adminuserinformation__user=request.user)

    fieldsets = (
        (
            None,
            {
                "description": '<p>Invitationer til en aktivitet laves nemmere via "person" oversigten. Gå derind og filtrer efter f.eks. børn på venteliste til din afdeling og sorter efter opskrivningsdato, eller filter medlemmer på forrige sæson. Herefter kan du vælge de personer på listen, du ønsker at invitere og vælge "Inviter alle valgte til en aktivitet" fra rullemenuen foroven.</p>',
                "fields": (
                    "person",
                    "activity",
                    "invite_dtm",
                    "expire_dtm",
                    "rejected_at",
                ),
            },
        ),
    )

    # Limit the activity possible to invite to: Not finished and belonging to user
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "activity" and not request.user.is_superuser:
            departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )
            kwargs["queryset"] = Activity.objects.filter(
                end_date__gt=timezone.now(), department__in=departments
            )
        return super(ActivityInviteAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def person_age_years(self, item):
        return item.person.age_years()

    person_age_years.short_description = "Alder"

    def person_zipcode(self, item):
        return item.person.zipcode

    person_zipcode.short_description = "Postnummer"

    def activity_department_union_link(self, item):
        url = reverse(
            "admin:members_union_change", args=[item.activity.department.union_id]
        )
        link = '<a href="%s">%s</a>' % (url, escape(item.activity.department.union.name))
        return mark_safe(link)

    activity_department_union_link.short_description = "Forening"
    activity_department_union_link.admin_order_field = (
        "activity__department__union__name"
    )

    def activity_department_link(self, item):
        url = reverse(
            "admin:members_department_change", args=[item.activity.department_id]
        )
        link = '<a href="%s">%s</a>' % (url, escape(item.activity.department.name))
        return mark_safe(link)

    activity_department_link.short_description = "Afdeling"
    activity_department_link.admin_order_field = "activity__department__name"

    def activity_link(self, item):
        url = reverse("admin:members_activity_change", args=[item.activity.id])
        link = '<a href="%s">%s</a>' % (url, item.activity.name)
        return mark_safe(link)

    activity_link.short_description = "Aktivitet"
    activity_link.admin_order_field = "activity__name"

    def person_link(self, item):
        url = reverse("admin:members_person_change", args=[item.person_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.person.name))
        return mark_safe(link)

    person_link.short_description = "Person"
    person_link.admin_order_field = "person__name"
