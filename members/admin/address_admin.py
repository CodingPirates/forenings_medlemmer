from django.contrib import admin
from members.models import Address
from members.forms.address_form import AddressForm

from members.models import (
    Union,
    Department,
    Activity,
)


class AddressUnionInline(admin.TabularInline):
    # Tabular Inline list of Unions using this address object. Read Only
    model = Union

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
        return regionList

    def queryset(self, request, queryset):
        region_id = request.GET.get(self.parameter_name, None)
        if region_id == "none":
            return queryset.filter(region="")
        if region_id:
            return queryset.filter(region=region_id)
        return queryset


class AddressAdmin(admin.ModelAdmin):
    form = AddressForm
    
    readonly_fields = (
        "created_at",
        "created_by",
        "dawa_id",
    )

    search_fields = (
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

    '''fields = (
        "search_address",
        "manual_entry",
        "streetname",
        "housenumber",
        "floor",
        "door",
        "placename",
        "zipcode",
        "city",
        "dawa_id",
    )'''

    # readonly_fields = ("dawa_id",)

    class Media:
        js = (
            "https://code.jquery.com/jquery-3.6.0.min.js",
            "https://code.jquery.com/ui/1.12.1/jquery-ui.min.js",  # Include jQuery UI
            "members/js/dawa-form-fill.js",  # This will contain the initialization code
            "members/js/dawa-autocomplete.js",
            "members/js/expand-dawa-info.js",
        )

        # Remove title for each record
        # see : https://stackoverflow.com/questions/41376406/remove-title-from-tabularinline-in-admin
        css = {
            "all": (
                "https://code.jquery.com/ui/1.12.1/themes/smoothness/jquery-ui.css",  # Include jQuery UI CSS
                "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css",  # Include Bootstrap CSS

                "members/css/custom_admin.css", # Include extra css to remove title for each record
            )
        }


    inlines = [AddressUnionInline, AddressDepartmentInline, AddressActivityInline]

    list_filter = (AddressRegionListFilter,)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["search_address"].widget.attrs.update({
            "id": "id_search_address",
            # "class": "textinput textInput ui-autocomplete-input",
            "class": "textinput textInput form-control ui-autocomplete-input"
        })
        form.base_fields["manual_entry"].widget.attrs.update({
            "id": "id_manual_entry",
            "class": "form-check-input", # manual-entry-checbox",
        })
        '''
        form.base_fields['housenumber'].widget.attrs['style'] = 'width: 5em;'
        form.base_fields['floor'].widget.attrs['style'] = 'width: 5em;'
        form.base_fields['door'].widget.attrs['style'] = 'width: 5em;'
        form.base_fields['zipcode'].widget.attrs['style'] = 'width: 5em;'
        '''
        return form
    def get_queryset(self, request):
        return Address.get_user_addresses(request.user)
    
    fieldsets = [
        (
            "Adresse",
            {
                "fields": (
                    (
                        "search_address",
                    ),
                    (
                        "manual_entry",
                    ),
                    (
                        "streetname",
                        "housenumber",
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
            #    "classes": ("collapse",),
            },
        ),
        (
            "Yderlige data",
            {
                "fields": ("created_at", "created_by"),
                "description": "Hvornår er denne adresse oprettet og af hvem ?",
            #    "classes": ("collapse",),
            },
        ),
    ]
