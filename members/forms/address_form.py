from django import forms
from members.models import Address

class AddressForm(forms.ModelForm):
    search_address = forms.CharField(
        label="Indtast adresse", required=False, max_length=200
    )

    manual_entry = forms.BooleanField(
        label="Indtast adresse felter manuelt", required=False
    )

    class Meta:
        model = Address
        fields = "__all__"
