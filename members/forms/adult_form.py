from django import forms
from django.conf import settings

from members.models.person import Person


class adultForm(forms.Form):
    parent_gender = forms.ChoiceField(
        label="Køn", required=True, choices=Person.MEMBER_ADULT_GENDER_CHOICES
    )
    parent_name = forms.CharField(label="Forældres navn", required=True, max_length=200)
    parent_birthday = forms.DateField(
        label="Forældres fødselsdato",
        input_formats=(settings.DATE_INPUT_FORMATS),
        error_messages={"invalid": "Indtast en gyldig dato."},
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    parent_email = forms.EmailField(label="Forældres private email", required=True)
    parent_phone = forms.CharField(
        label="Forældres telefon", required=True, max_length=50
    )
