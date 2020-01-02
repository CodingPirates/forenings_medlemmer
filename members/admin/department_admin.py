from django.contrib import admin

from members.models import Union, Address


class UnionDepartmentFilter(admin.SimpleListFilter):
    title = "Forening"
    parameter_name = "Union"

    def lookups(self, request, model_admin):
        unions = Union.objects.all()
        union_list = []
        for union in unions:
            union_list.append((str(union.pk), str(union)))
        return union_list

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(union=self.value())


class DepartmentAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(DepartmentAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["address"].queryset = Address.get_user_addresses(request.user)
        return form

    list_filter = (UnionDepartmentFilter,)
    raw_id_fields = ("union",)
    # Only show own departments

    def get_queryset(self, request):
        qs = super(DepartmentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
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
        ("Ansvarlig", {"fields": ("responsible_name", "responsible_contact")}),
        (
            "Adresse",
            {
                "fields": (
                    "streetname",
                    "housenumber",
                    "floor",
                    "door",
                    "zipcode",
                    "city",
                    "placename",
                )
            },
        ),
        ("Adresse-New", {"fields": ("address",)},),
        (
            "Længde og Breddegrad",
            {
                "fields": ("longitude", "latitude"),
                "description": "<p>Hvis de ikke er sat opdateres de automatisk på et tidspunkt",
            },
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
                "fields": ("has_waiting_list", "created", "closed_dtm"),
                "description": "<p>Venteliste betyder at børn har mulighed for at skrive sig på ventelisten (tilkendegive interesse for denne afdeling). Den skal typisk altid være krydset af.</p>",
                "classes": ("collapse",),
            },
        ),
    ]
    list_display = ("name", "address")
