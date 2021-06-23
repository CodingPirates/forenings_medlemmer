from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Hidden, Div

from members.models.department import Department


class vol_emailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(vol_emailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "volunteer_email"
        self.helper.html5_required = True
        self.fields["volunteer_birthday"].widget.format = "%d-%m-%Y"
        self.helper.layout = Layout(
            Hidden("form_id", "vol_email", id="id_form_id"),
            Fieldset(
                "Frivilliges oplysninger",
                Div(
                    Div(Field("volunteer_email"), css_class="col-md-5"),
                    Div(Field("volunteer_name"), css_class="col-md-5"),
                    Div(Field("volunteer_zipcode"), css_class="col-md-5"),
                    Div(Field("volunteer_city"), css_class="col-md-5"),
                    Div(Field("volunteer_phone"), css_class="col-md-5"),
                    Div(Field("volunteer_birthday"), css_class="col-md-5"),
                    Div(Field("volunteer_department"), css_class="col-md-5"),
                    css_class="row",
                ),
            ),
            Submit("submit", "Opret", css_class="btn-success"),
        )

    volunteer_name = forms.CharField(
        label="Dit fulde navn", required=True, max_length=200
    )
    volunteer_email = forms.EmailField(label="Email", required=True)
    volunteer_phone = forms.CharField(label="Telefon", required=True, max_length=50)
    volunteer_birthday = forms.DateField(
        label="Fødselsdato (dd-mm-åååå)",
        required=True,
        input_formats=(settings.DATE_INPUT_FORMATS),
        error_messages={"invalid": "Indtast en gyldig dato."},
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    volunteer_department = forms.ModelChoiceField(
        queryset=Department.objects.filter(closed_dtm__isnull=True),
        required=True,
        label="Afdeling",
        empty_label="-",
    )

    volunteer_zipcode = forms.CharField(
        label="Postnummer", max_length=4.0, required=True
    )
    volunteer_city = forms.CharField(label="By", max_length=200, required=True)
    form_id = forms.CharField(
        label="Form ID", max_length=10, widget=forms.HiddenInput(), initial="signup"
    )
