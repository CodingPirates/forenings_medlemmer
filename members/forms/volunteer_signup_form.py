from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Hidden, Div

from members.models.department import Department
from members.models.person import Person

from django.contrib.auth.password_validation import validate_password


class vol_signupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(vol_signupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "volunteer_signup"
        self.helper.html5_required = True
        self.fields["volunteer_birthday"].widget.format = "%d-%m-%Y"
        self.helper.layout = Layout(
            Hidden("form_id", "vol_signup", id="id_form_id"),
            Fieldset(
                "Frivilliges oplysninger",
                Div(
                    Div(Field("volunteer_gender"), css_class="col-md-2"),
                    Div(Field("volunteer_name"), css_class="col-md-10"),
                    Div(
                        Field(
                            "volunteer_birthday",
                        ),
                        css_class="col-md-3",
                    ),
                    Div(Field("volunteer_email"), css_class="col-md-3"),
                    Div(Field("volunteer_phone"), css_class="col-md-3"),
                    Div(Field("volunteer_department"), css_class="col-md-3"),
                    css_class="row",
                ),
            ),
            Fieldset(
                "Adgangskode",
                Div(
                    Div(Field("password1"), css_class="col"),
                    Div(Field("password2"), css_class="col"),
                    css_class="row",
                ),
            ),
            Fieldset(
                "Adresse oplysninger",
                Div(
                    Div(
                        Field("search_address", id="search-address"),
                        css_class="col-md-10",
                    ),
                    Div(Field("manual_entry", id="manual-entry"), css_class="col-md-2"),
                    Div(
                        Field(
                            "streetname", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-9",
                    ),
                    Div(
                        Field(
                            "housenumber", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("floor", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("door", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("zipcode", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-2",
                    ),
                    Div(
                        Field("city", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-5",
                    ),
                    Div(
                        Field(
                            "placename", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-5",
                    ),
                    Hidden("dawa_id", "", id="id_dawa_id"),
                    css_class="row",
                ),
            ),
            Submit("submit", "Opret", css_class="btn-success"),
        )

    volunteer_gender = forms.ChoiceField(
        label="Køn", required=True, choices=Person.MEMBER_ADULT_GENDER_CHOICES
    )
    volunteer_name = forms.CharField(label="Fulde navn", required=True, max_length=200)
    volunteer_email = forms.EmailField(label="Email", required=True)
    volunteer_phone = forms.CharField(label="Telefon", required=True, max_length=50)
    volunteer_birthday = forms.DateField(
        label="Fødselsdato",
        required=True,
        input_formats=(settings.DATE_INPUT_FORMATS),
        error_messages={"invalid": "Indtast en gyldig dato."},
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    volunteer_department = forms.ModelChoiceField(
        queryset=Department.objects.filter(closed_dtm__isnull=True).order_by("name"),
        required=True,
        label="Afdeling",
        empty_label="-",
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(),
        label="Adgangskode",
        required=True,
        max_length=20,
        validators=[validate_password],
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(),
        label="Gentag adgangskode",
        required=True,
        max_length=20,
    )

    search_address = forms.CharField(
        label="Indtast adresse", required=False, max_length=200
    )
    streetname = forms.CharField(label="Vejnavn", required=True, max_length=200)
    housenumber = forms.CharField(label="Nummer", required=True, max_length=5)
    floor = forms.CharField(label="Etage", required=False, max_length=3)
    door = forms.CharField(label="Dør", required=False, max_length=5)
    placename = forms.CharField(label="Stednavn", required=False, max_length=200)
    zipcode = forms.CharField(label="Postnummer", max_length=4.0, required=True)
    city = forms.CharField(label="By", max_length=200, required=True)
    dawa_id = forms.CharField(
        label="Dawa ID", max_length=200, widget=forms.HiddenInput(), required=False
    )
    form_id = forms.CharField(
        label="Form ID", max_length=10, widget=forms.HiddenInput(), initial="signup"
    )
    manual_entry = forms.ChoiceField(
        label="Indtast felter manuelt",
        widget=forms.CheckboxInput,
        required=False,
        choices=((True, "True"), (False, "False")),
    )
