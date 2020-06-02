from django import forms
from django.conf import settings

from members.models.person import Person


class childForm(forms.Form):
    child_gender = forms.ChoiceField(
        label="Køn", required=True, choices=Person.MEMBER_GENDER_CHOICES
    )
    child_name = forms.CharField(
        label="Barns fulde navn", required=True, max_length=200
    )
    child_birthday = forms.DateField(
        label="Barns fødselsdato",
        input_formats=(settings.DATE_INPUT_FORMATS),
        widget=forms.DateInput(attrs={"type": "date"}),
        error_messages={"invalid": "Indtast en gyldig dato"},
    )
    child_email = forms.EmailField(label="Barns email", required=False)
    child_phone = forms.CharField(label="Barns telefon", required=False, max_length=50)
