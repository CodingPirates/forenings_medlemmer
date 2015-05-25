from django import forms
from members.models import Person
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField, Field, Hidden
from crispy_forms.bootstrap import StrictButton

class PersonForm(forms.ModelForm):
    class Meta:
        model=Person
        fields= ['name','zipcode','city', 'streetname', 'housenumber', 'floor', 'door', 'placename', 'email','phone']

class getLoginForm(forms.Form):
    email = forms.EmailField(required=True, label="Email", initial="din@email.dk", help_text="Indtast den email adresse du oprindeligt opskrev dig med.", error_messages={'required': 'Indtast din email adresse først', 'invalid' : 'Ikke en gyldig email adresse!'})

class getSignupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(getSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-getSignupForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'entry_page'
        self.helper.help_text_inline = False
        self.helper.html5_required = True
        self.helper.layout = Layout(
            MultiField('Barnets oplysninger',
                     'child_name',
                     'child_email',
                     'child_phone',
                     Field('child_birthday', css_class="datepicker")),
            Fieldset('Forældres oplysninger',
                     'parent_name',
                     'parent_email',
                     'parent_phone'
                     ),
            Fieldset('Adresse oplysninger',
                     Field('search_address', id="search-address"),
                     Field('streetname', readonly=True),
                     Field('housenumber', readonly=True),
                     Field('floor', readonly=True),
                     Field('door', readonly=True),
                     Field('placename', readonly=True),
                     Field('zipcode', readonly=True),
                     Field('city', readonly=True),
                     Hidden('dawa_id', '')
                     )

        )
        self.helper.add_input(Submit('submit', 'Submit'))

    child_name = forms.CharField(label='Barns navn', required=True, max_length=200)
    child_email = forms.EmailField(label='Barns email', required=False)
    child_phone = forms.CharField(label='Barns telefon', required=False, max_length=50)
    child_birthday = forms.DateField(label='Barns fødselsdato', required=True)

    parent_name = forms.CharField(label='Forældres navn', required=True, max_length=200)
    parent_email = forms.EmailField(label='Forældres email', required=True)
    parent_phone = forms.CharField(label='Forældres telefon', required=True, max_length=50)

    search_address = forms.CharField(label='Indtast adresse', required=True, max_length=200)
    streetname = forms.CharField(label='Vejnavn', required=True, max_length=200)
    housenumber = forms.CharField(label='Husnummer', required=True, max_length=5)
    floor = forms.CharField(label='Etage', required=False,max_length=3)
    door = forms.CharField(label='Dør', required=False,max_length=5)
    placename = forms.CharField(label='Stednavn', required=False,max_length=200)
    zipcode = forms.CharField(label='Postnummer', max_length=4)
    city = forms.CharField(label='By', max_length=200, required=False)
    dawa_id = forms.CharField()
