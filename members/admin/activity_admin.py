from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape

from members.models import (
    ActivityParticipant,
    AdminUserInformation,
    Department,
    Union,
)

from members.admin.admin_actions import AdminActions


class ActivityParticipantInline(admin.TabularInline):
    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    model = ActivityParticipant
    extra = 0
    classes = ["hideheader"]
    fields = (
        "person",
        "note",
        "photo_permission",
        "payment_info_html",
    )
    readonly_fields = fields
    can_delete = False

    def get_queryset(self, request):
        return ActivityParticipant.objects.all().order_by("person")


class ActivityUnionListFilter(admin.SimpleListFilter):
    title = "Lokalforeninger"
    parameter_name = "department__union"

    def lookups(self, request, model_admin):
        unions = []
        for union1 in (
            Union.objects.filter(
                department__union__in=AdminUserInformation.get_unions_admin(
                    request.user
                )
            )
            .order_by("name")
            .distinct()
        ):
            unions.append((str(union1.pk), str(union1.name)))
        return unions

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(department__union__pk=self.value())


class ActivityDepartmentListFilter(admin.SimpleListFilter):
    title = "Afdelinger"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        departments = []
        for department1 in (
            Department.objects.filter(
                activity__department__in=AdminUserInformation.get_departments_admin(
                    request.user
                )
            )
            .order_by("name")
            .distinct()
        ):
            departments.append((str(department1.pk), str(department1)))
        return departments

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(department__pk=self.value())


class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "union_link",
        "department_link",
        "activitytype",
        "start_end",
        "open_invite",
        "price_in_dkk",
        "seats_total",
        "seats_used",
        "seats_free",
        "age",
    )

    date_hierarchy = "start_date"
    search_fields = (
        "name",
        "department__union__name",
        "department__name",
        "description",
    )
    readonly_fields = ("seats_left", "participants")
    list_per_page = 20
    raw_id_fields = (
        "union",
        "department",
    )
    list_filter = (
        ActivityUnionListFilter,
        ActivityDepartmentListFilter,
        "open_invite",
        "activitytype",
    )
    actions = [
        AdminActions.export_participants_csv,
    ]
    save_as = True

    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    inlines = [ActivityParticipantInline]

    def start_end(self, obj):
        return str(obj.start_date) + " - " + str(obj.end_date)

    start_end.short_description = "Periode"
    start_end.admin_order_field = "start_date"

    def age(self, obj):
        return str(obj.min_age) + " - " + str(obj.max_age)

    age.short_description = "Alder"
    age.admin_order_field = "min_age"

    def union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.department.union_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.department.union.name))
        return mark_safe(link)

    union_link.short_description = "Forening"
    union_link.admin_order_field = "department__union__name"

    def department_link(self, item):
        url = reverse("admin:members_department_change", args=[item.department_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.department.name))
        return mark_safe(link)

    department_link.short_description = "Afdeling"
    department_link.admin_order_field = "department__name"

    def seats_total(self, obj):
        return str(obj.max_participants)

    seats_total.short_description = "Total"
    seats_total.admin_order_field = "max_participants"

    def seats_used(self, obj):
        return str(obj.activityparticipant_set.count())

    seats_used.short_description = "Besat"

    def seats_free(self, obj):
        return str(obj.max_participants - obj.activityparticipant_set.count())

    seats_free.short_description = "Ubesat"

    def activity_membership_union_link(self, obj):
        if obj.activitytype_id in ["FORENINGSMEDLEMSKAB", "STØTTEMEDLEMSKAB"]:
            url = reverse("admin:members_union_change", args=[obj.union_id])
            link = '<a href="%s">%s</a>' % (url, escape(obj.union.name))
            return mark_safe(link)
        else:
            return ""

    activity_membership_union_link.short_description = "Forening for medlemskab"

    # Only view activities on own department
    def get_queryset(self, request):
        qs = super(ActivityAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
            return qs
        departments = Department.objects.filter(adminuserinformation__user=request.user)
        return qs.filter(department__in=departments)

    # Only show own departments when creating new activity
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if (
            db_field.name == "department"
            and not request.user.is_superuser
            and not request.user.has_perm("members.view_all_departments")
        ):
            kwargs["queryset"] = Department.objects.filter(
                adminuserinformation__user=request.user
            )
        return super(ActivityAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    fieldsets = [
        (
            "Afdeling",
            {
                "description": "<p>Du kan ændre afdeling for aktiviteten ved at skrive afdelings-id, eller tryk på søg-ikonet og i det nye vindue skal du finde afdelingen, for derefter at trykke på ID i første kolonne.</p>",
                "fields": ("department",),
            },
        ),
        (
            "Aktivitet",
            {
                "description": "<p>Aktivitetsnavnet skal afspejle aktivitet samt tidspunkt. F.eks. <em>Forårssæson 2018</em>.</p><p>Tidspunkt er f.eks. <em>Onsdage 17:00-19:00</em></p>",
                "fields": (
                    (
                        "name",
                        "activitytype",
                    ),
                    "open_hours",
                    "description",
                    (
                        "start_date",
                        "end_date",
                    ),
                    "member_justified",
                ),
            },
        ),
        (
            "Lokation og ansvarlig",
            {
                "description": "<p>Adresse samt ansvarlig kan adskille sig fra afdelingens informationer (f.eks. et gamejam der foregår et andet sted).</p>",
                "fields": (
                    (
                        "responsible_name",
                        "responsible_contact",
                    ),
                    (
                        "streetname",
                        "housenumber",
                        "floor",
                        "door",
                    ),
                    (
                        "zipcode",
                        "city",
                        "placename",
                    ),
                ),
            },
        ),
        (
            "Tilmeldingsdetaljer",
            {
                "description": '<p>Tilmeldingsinstruktioner er tekst der kommer til at stå på betalingsformularen på tilmeldingssiden. Den skal bruges til at stille spørgsmål, som den, der tilmelder sig, kan besvare ved tilmelding.</p><p>Fri tilmelding betyder, at alle, når som helst kan tilmelde sig denne aktivitet - efter "først til mølle"-princippet. Dette er kun til aktiviteter og klubaften-forløb/sæsoner i områder, hvor der ikke er nogen venteliste. </p><p>Alle aktiviteter med fri tilmelding kommer til at stå med en stor "tilmeld" knap på medlemssiden. <b>Vi bruger typisk ikke fri tilmelding - spørg i Slack hvis du er i tvivl!</b></p>',
                "fields": (
                    "instructions",
                    (
                        "signup_closing",
                        "open_invite",
                    ),
                    "price_in_dkk",
                    (
                        "max_participants",
                        "participants",
                        "seats_left",
                    ),
                    (
                        "min_age",
                        "max_age",
                    ),
                ),
            },
        ),
    ]
