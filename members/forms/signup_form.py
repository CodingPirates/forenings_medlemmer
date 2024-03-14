from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Hidden, Div

from members.models.person import Person

from django.contrib.auth.password_validation import validate_password


class signupForm(forms.Form):
    def __init__(self, next_url=None, *args, **kwargs):
        """
        Args:
            next_url (str): Optional url that user will be redirected to after account creation and login.
                            Note: The user still needs to login, but will then be redirected to this url.
        """
        super(signupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "account_create"
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Hidden("form_id", "signup", id="id_form_id"),
            Hidden("next", next_url if next_url is not None else "", id="id_next"),
            Fieldset(
                "Barnets oplysninger",
                Div(
                    Div(Field("child_gender"), css_class="col-md-2"),
                    Div(Field("child_name"), css_class="col-md-10"),
                    Div(
                        Field(
                            "child_birthday",
                        ),
                        css_class="col-md-4",
                    ),
                    Div(Field("child_email"), css_class="col-md-4"),
                    Div(Field("child_phone"), css_class="col-md-4"),
                    css_class="row",
                ),
            ),
            Fieldset(
                "Forældres oplysninger",
                Div(
                    Div(Field("parent_gender"), css_class="col-md-2"),
                    Div(Field("parent_name"), css_class="col-md-10"),
                    Div(
                        Field(
                            "parent_birthday",
                        ),
                        css_class="col-md-4",
                    ),
                    Div(Field("parent_email"), css_class="col-md-4"),
                    Div(Field("parent_phone"), css_class="col-md-4"),
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

    child_gender = forms.ChoiceField(
        label="Køn", required=True, choices=Person.MEMBER_GENDER_CHOICES
    )
    child_name = forms.CharField(
        label="Barns fulde navn", required=True, max_length=200
    )
    child_email = forms.EmailField(label="Barns email", required=False)
    child_phone = forms.CharField(label="Barns telefon", required=False, max_length=50)
    child_birthday = forms.DateField(
        label="Barns fødselsdato",
        input_formats=(settings.DATE_INPUT_FORMATS),
        widget=forms.DateInput(attrs={"type": "date"}),
        error_messages={"invalid": "Indtast en gyldig dato"},
    )
    parent_gender = forms.ChoiceField(
        label="Køn", required=True, choices=Person.MEMBER_ADULT_GENDER_CHOICES
    )
    parent_name = forms.CharField(label="Forældres navn", required=True, max_length=200)
    parent_email = forms.EmailField(label="Forældres private email", required=True)
    parent_phone = forms.CharField(
        label="Forældres telefon", required=True, max_length=50
    )
    parent_birthday = forms.DateField(
        label="Forældres fødselsdato",
        input_formats=(settings.DATE_INPUT_FORMATS),
        error_messages={"invalid": "Indtast en gyldig dato."},
        widget=forms.DateInput(attrs={"type": "date"}),
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
