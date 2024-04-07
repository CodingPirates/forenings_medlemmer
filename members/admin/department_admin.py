from django.contrib import admin
from django.db.models.functions import Upper
from django.urls import reverse
from django.utils.safestring import mark_safe
from members.models import Union, Address, Person
from django.utils.html import escape


class UnionDepartmentFilter(admin.SimpleListFilter):
    title = "Forening"
    parameter_name = "Union"

    def lookups(self, request, model_admin):
        return [(str(union.pk), str(union.name)) for union in Union.objects.all()]

    def queryset(self, request, queryset):
        return queryset if self.value() is None else queryset.filter(union=self.value())


class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "department_union_link",
        "department_link",
        "address",
        "isVisible",
        "isOpening",
        "created",
        "closed_dtm",
        "waitinglist_count_link",
    )
    list_filter = (
        "address__region",
        UnionDepartmentFilter,
        "isVisible",
        "isOpening",
        "created",
        "closed_dtm",
    )
    raw_id_fields = ("union",)
    search_fields = (
        "name",
        "union__name",
        "address__streetname",
        "address__housenumber",
        "address__placename",
        "address__zipcode",
        "address__city",
    )
    filter_horizontal = ["department_leaders"]

    # Solution found on https://stackoverflow.com/questions/57056994/django-model-form-with-only-view-permission-puts-all-fields-on-exclude
    # formfield_for_foreignkey described in documentation here: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.formfield_for_foreignkey
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "address":
            kwargs["queryset"] = Address.get_user_addresses(request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "department_leaders":
            kwargs["queryset"] = Person.objects.filter(user__is_staff=True).order_by(
                Upper("name")
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(DepartmentAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
            return qs
        return qs.filter(adminuserinformation__user=request.user)

    fieldsets = [
        (
            "Beskrivelse",
            {
                "fields": ("name", "union", "description", "open_hours"),
                "description": "<p>Lav en beskrivelse af jeres aktiviteter, teknologier og tekniske niveau.</p><p>Åbningstid er ugedag samt tidspunkt<p>",
            },
        ),
        (
            "Ansvarlig",
            {"fields": ("responsible_name", "department_email", "department_leaders")},
        ),
        (
            "Adresse",
            {"fields": ("address",)},
        ),
        (
            "Afdelingssiden",
            {
                "fields": ("website", "isOpening", "isVisible"),
                "description": "<p>Har kan du vælge om afdeling skal vises på codingpirates.dk/afdelinger og om der skal være et link til en underside</p>",
            },
        ),
        (
            "Yderlige data",
            {
                "fields": ("created", "closed_dtm"),
                "description": "<p>Venteliste betyder at børn har mulighed for at skrive sig på ventelisten (tilkendegive interesse for denne afdeling). Den skal typisk altid være krydset af.</p>",
                "classes": ("collapse",),
            },
        ),
    ]

    def department_union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.union_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.union.name))
        return mark_safe(link)

    department_union_link.short_description = "Forening"
    department_union_link.admin_order_field = "union__name"

    def department_link(self, item):
        url = reverse("admin:members_department_change", args=[item.id])
        link = '<a href="%s">%s</a>' % (url, escape(item.name))
        return mark_safe(link)

    department_link.short_description = "Afdeling"
    department_link.admin_order_field = "name"

    def waitinglist_count_link(self, item):
        admin_url = reverse("admin:members_waitinglist_changelist")
        link = f"""<a
            href="{admin_url}?waiting_list={item.id}"
            title="Vis venteliste for afdelingen Coding Pirates {item.name}">
            {item.waitinglist_set.count()}
            </a>"""
        return mark_safe(link)

    waitinglist_count_link.short_description = "Venteliste"
