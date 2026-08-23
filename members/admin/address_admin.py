from django.conf import settings
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from members.models import (
    Activity,
    Address,
    Department,
    Union,
)


class ReadOnlyInlineFormSet(BaseInlineFormSet):
    """Skip validation for unchanged read-only inline rows.

    Address admin only shows related objects for context; they are not editable
    from this screen. Marking existing inline forms as empty-permitted avoids
    triggering model validation for unrelated child objects when the address
    itself is saved.
    """

    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        form.empty_permitted = True
        return form


class AddressUnionInline(admin.TabularInline):
    # Tabular Inline list of Unions using this address object. Read Only
    model = Union
    formset = ReadOnlyInlineFormSet

    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    classes = ["hideheader"]
    extra = 0
    fields = ("name",)
    readonly_fields = fields
    can_delete = False

    def get_queryset(self, request):
        return Union.objects.all().order_by("name")

    def has_add_permission(self, request, obj=None):
        return False


class AddressDepartmentInline(admin.TabularInline):
    # Tabular Inline list of Departments using this address object. Read Only
    model = Department
    formset = ReadOnlyInlineFormSet

    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    classes = ["hideheader"]
    extra = 0
    fields = ("name",)
    readonly_fields = fields
    can_delete = False

    def get_queryset(self, request):
        return Department.objects.all().order_by("name")

    def has_add_permission(self, request, obj=None):
        return False


class AddressActivityInline(admin.TabularInline):
    # Tabular Inline list of Activities using this address object. Read Only
    model = Activity
    formset = ReadOnlyInlineFormSet

    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    classes = ["hideheader"]
    extra = 0
    fields = (
        "name",
        "start_date",
        "end_date",
        "department",
    )
    readonly_fields = fields
    can_delete = False

    def get_queryset(self, request):
        return Activity.objects.all().order_by("name")

    def has_add_permission(self, request, obj=None):
        return False


class AddressRegionListFilter(admin.SimpleListFilter):
    # List filter on region values
    title = "Regioner"
    parameter_name = "region"

    def lookups(self, request, model_admin):
        regionList = [("none", "(ingen region)")]
        lastRegion = ""
        for aRegion in Address.objects.all().order_by("region"):
            if aRegion.region != lastRegion:
                lastRegion = aRegion.region
                regionList += (
                    (
                        str(aRegion.region),
                        str(aRegion.region),
                    ),
                )

        if len(regionList) <= 1:
            return ()

        return regionList

    def queryset(self, request, queryset):
        region_id = request.GET.get(self.parameter_name, None)
        if region_id == "none":
            return queryset.filter(region="")
        if region_id:
            return queryset.filter(region=region_id)
        return queryset


class AddressAdmin(admin.ModelAdmin):
    list_per_page = settings.LIST_PER_PAGE

    readonly_fields = (
        "created_at",
        "created_by",
    )

    search_fields = (
        "streetname",
        "housenumber",
        "floor",
        "door",
        "placename",
        "zipcode",
        "city",
        "region",
        "descriptiontext",
        "dawa_id",
    )

    list_display = (
        "id",
        "streetname",
        "housenumber",
        "floor",
        "door",
        "placename",
        "zipcode",
        "city",
        "region",
        "descriptiontext",
        "dawa_id",
        "dawa_category",
    )

    class Media:
        # Remove title for each record
        # see : https://stackoverflow.com/questions/41376406/remove-title-from-tabularinline-in-admin
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    inlines = [AddressUnionInline, AddressDepartmentInline, AddressActivityInline]

    list_filter = (AddressRegionListFilter,)

    def get_queryset(self, request):
        return Address.get_user_addresses(request.user)

    fieldsets = [
        (
            "Adresse",
            {
                "fields": (
                    (
                        "streetname",
                        "housenumber",
                    ),
                    (
                        "floor",
                        "door",
                    ),
                    "placename",
                    (
                        "zipcode",
                        "city",
                    ),
                    (
                        "municipality",
                        "region",
                    ),
                    "descriptiontext",
                )
            },
        ),
        (
            "Dawa info",
            {
                "description": """
                    <p>ID, kategori, længde- og breddegrad fra DAWA.</p>
                    <p>Du kan vælge at sætte egne værdier for længde- og breddegrad.</p>""",
                "fields": (
                    (
                        "dawa_id",
                        "dawa_category",
                    ),
                    "dawa_overwrite",
                    (
                        "longitude",
                        "latitude",
                    ),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Yderlige data",
            {
                "fields": ("created_at", "created_by"),
                "description": "Hvornår er denne adresse oprettet og af hvem ?",
                "classes": ("collapse",),
            },
        ),
    ]
