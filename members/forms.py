from django import forms
from members.models import Person

class PersonForm(forms.ModelForm):
    class Meta:
        model=Person
        fields= ['name','zipcode','city', 'streetname', 'housenumber', 'floor', 'door', 'placename', 'email','phone']

class getLoginForm(forms.Form):
    email = forms.EmailField(required=True, label="Email", initial="din@email.dk", help_text="Indtast den email adresse du oprindeligt opskrev dig med.", error_messages={'required': 'Indtast din email adresse først', 'invalid' : 'Ikke en gyldig email adresse!'})
