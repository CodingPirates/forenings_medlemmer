from django import forms
from crispy_forms.layout import Fieldset, Div, Field

from .base_volunteer_request_form import BaseVolunteerRequestForm


class VolunteerRequestForm(BaseVolunteerRequestForm):
    """Form for non-authenticated users to request volunteer opportunities"""

    class Meta(BaseVolunteerRequestForm.Meta):
        fields = [
            "name",
            "email",
            "phone",
            "age",
            "zip",
            "info_reference",
            "info_whishes",
        ]

    # Additional fields for non-authenticated users
    name = forms.CharField(label="Navn", required=True, max_length=200)
    email = forms.EmailField(label="Email", required=True, max_length=254)
    phone = forms.CharField(label="Telefon", required=True, max_length=50)
    age = forms.IntegerField(label="Alder", required=False)
    zip = forms.CharField(label="Postnummer", required=False, max_length=4)

    def __init__(self, *args, **kwargs):
        super(VolunteerRequestForm, self).__init__(*args, **kwargs)

        # Make basic personal fields required
        for field_name in ["name", "email", "phone"]:
            self.fields[field_name].required = True

        # Setup the layout
        self.setup_layout()

    def get_basic_fieldset(self):
        """Override to include personal information fields"""
        return Fieldset(
            "Grundlæggende oplysninger",
            Div(
                Div(Field("name"), css_class="col-md-6"),
                Div(Field("email"), css_class="col-md-6"),
                css_class="row",
            ),
            Div(
                Div(Field("phone"), css_class="col-md-4"),
                Div(Field("age"), css_class="col-md-4"),
                Div(Field("zip"), css_class="col-md-4"),
                css_class="row",
            ),
            Div(
                Field("info_reference"),
                css_class="col-md-12",
            ),
            Div(
                Field("info_whishes"),
                css_class="col-md-12",
            ),
        )
