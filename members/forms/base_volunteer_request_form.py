from django import forms
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Div, HTML

from members.models.volunteerrequest import VolunteerRequest
from members.models.department import Department
from members.models.activity import Activity


class ActivityCheckboxWidget(forms.CheckboxSelectMultiple):
    """Custom widget that renders activity checkboxes with clickable links"""

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )

        # Debug: Print to console what we're working with
        print(f"ActivityCheckboxWidget - value: {value}, label: {label}")

        if value and str(value).isdigit():
            try:
                # Convert value to int if it's not already
                activity_id = int(value)
                activity = Activity.objects.get(pk=activity_id)
                activity_url = reverse(
                    "activity_view", kwargs={"activity_id": activity.id}
                )

                print(f"Creating link for activity {activity_id}: {activity_url}")

                # Use the existing label text but wrap it in a link
                if option["label"]:
                    label_text = str(option["label"])
                    link_html = f'<a href="{activity_url}" target="_blank" rel="noopener noreferrer">{label_text}</a>'
                    option["label"] = mark_safe(link_html)
                    print(f"Final label: {option['label']}")

            except (Activity.DoesNotExist, ValueError, TypeError) as e:
                # Fall back to the original label if there's any issue
                print(f"Error creating activity link: {e}")
                pass
        else:
            print(f"Skipping value: {value} (not digit or empty)")

        return option


class DepartmentWithAddressChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        """Custom label that includes department name and address"""
        address = obj.address
        return f"{obj.name} ({address.streetname} {address.housenumber}, {address.zipcode} {address.city})"


class ActivityWithAddressAndLinkChoiceField(forms.ModelMultipleChoiceField):
    """Custom field that includes activity name, department, address, and creates clickable links"""

    def __init__(self, *args, **kwargs):
        kwargs["widget"] = ActivityCheckboxWidget()
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """Custom label that includes activity name, department, and address"""
        address = obj.address
        activity_url = reverse("activity_view", kwargs={"activity_id": obj.id})
        display_text = f"{obj.department.name}: {obj.name} ({address.streetname} {address.housenumber}, {address.zipcode} {address.city})"
        return mark_safe(
            f'<a href="{activity_url}" target="_blank" rel="noopener noreferrer">{display_text}</a>'
        )


class BaseVolunteerRequestForm(forms.ModelForm):
    """Base form with shared functionality for volunteer requests"""

    class Meta:
        model = VolunteerRequest
        fields = ["info_reference", "info_whishes"]
        widgets = {
            "info_reference": forms.Textarea(attrs={"rows": 3}),
            "info_whishes": forms.Textarea(attrs={"rows": 5}),
        }

    # Shared fields for departments and activities
    departments = DepartmentWithAddressChoiceField(
        queryset=Department.objects.filter(closed_dtm__isnull=True).order_by("name"),
        widget=forms.CheckboxSelectMultiple,
        label="Afdelinger",
        help_text="Vælg hvilke afdelinger du er interesseret i at være frivillig for",
        required=False,
    )

    activities = ActivityWithAddressAndLinkChoiceField(
        queryset=Activity.objects.filter(
            activitytype__in=["FORLØB", "ARRANGEMENT"],
            end_date__gte=timezone.now().date(),
        ).order_by("department__name", "name"),
        label="Aktiviteter",
        help_text="Vælg specifikke aktiviteter du er interesseret i at hjælpe med (klik på linket for at se mere information)",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(BaseVolunteerRequestForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "volunteer_signup"
        self.helper.html5_required = True

        # Make info fields required
        self.fields["info_reference"].required = True
        self.fields["info_whishes"].required = True

    def clean(self):
        cleaned_data = super().clean()
        departments = cleaned_data.get("departments")
        activities = cleaned_data.get("activities")

        # Ensure at least one department or activity is selected
        if not departments and not activities:
            raise forms.ValidationError(
                "Du skal vælge mindst én afdeling eller aktivitet du er interesseret i."
            )

        return cleaned_data

    def get_basic_fieldset(self):
        """Override in subclasses to define the basic information fieldset"""
        return Fieldset(
            "Frivillig oplysninger",
            Div(
                Field("info_reference"),
                css_class="col-md-12",
            ),
            Div(
                Field("info_whishes"),
                css_class="col-md-12",
            ),
        )

    def get_layout(self):
        """Get the complete form layout"""
        return Layout(
            self.get_basic_fieldset(),
            Fieldset(
                "Interesse områder",
                HTML(
                    """
                    <div class="mb-3">
                        <label for="search-filter" class="form-label">Søg efter afdeling eller aktivitet:</label>
                        <input
                            type="text"
                            id="search-filter"
                            class="form-control"
                            onkeyup="filter_volunteer_checkboxes()"
                            placeholder="Søg efter afdelingsnavn, aktivitetsnavn, by, postnummer, gade..."
                        />
                    </div>
                """
                ),
                Div(
                    Field("departments"),
                    css_class="col-md-6",
                ),
                Div(
                    Field("activities"),
                    css_class="col-md-6",
                ),
                css_class="row",
            ),
            Submit("submit", "Send anmodning", css_class="btn-success"),
        )

    def setup_layout(self):
        """Setup the crispy forms layout"""
        self.helper.layout = self.get_layout()
