from django import forms
from django.conf import settings

from members.models.person import Person


class signupForm(forms.Form):
    password1 = forms.CharField(
        label="Kodeord", required=True, widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Gentag kodeord", required=True, widget=forms.PasswordInput
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
