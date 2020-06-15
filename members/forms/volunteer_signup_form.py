from django import forms
from django.conf import settings

from members.models.department import Department
from members.models.person import Person


class volunteerForm(forms.Form):
    volunteer_gender = forms.ChoiceField(
        label="Køn", required=True, choices=Person.MEMBER_ADULT_GENDER_CHOICES
    )
    volunteer_name = forms.CharField(label="Fulde navn", required=True, max_length=200)
    volunteer_birthday = forms.DateField(
        label="Fødselsdato (dd-mm-åååå)",
        required=True,
        input_formats=(settings.DATE_INPUT_FORMATS),
        error_messages={"invalid": "Indtast en gyldig dato."},
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    volunteer_email = forms.EmailField(label="Email", required=True)
    volunteer_phone = forms.CharField(label="Telefon", required=True, max_length=50)
    volunteer_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        label="Afdeling",
        empty_label="-",
    )
