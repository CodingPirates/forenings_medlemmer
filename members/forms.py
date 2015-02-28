from django import forms
from members.models import Person

class PersonForm(forms.ModelForm):
    class Meta:
        model=Person
        fields= ['membertype', 'name','street','placename','zipcity','email','phone','on_waiting_list']
