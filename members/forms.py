from django import forms
from django.conf import settings
from members.models import Person
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField, Field, Hidden, HTML, Div, Button

class PersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True
        if self.instance != None and self.instance.membertype == Person.CHILD:
            nameFieldSet = Fieldset('Barnets oplysninger',
                    Div(
                         Div(Field('name'), css_class="col-md-12"),
                         Div(Field('birthday', css_class="datepicker", input_formats=(settings.DATE_INPUT_FORMATS)), css_class="col-md-4"),
                         Div(Field('email'), css_class="col-md-4"),
                         Div(Field('phone'), css_class="col-md-4"),
                         css_class="row"
                       )
                )
            self.fields['birthday'].widget.format = '%d-%m-%Y'
        else:
            nameFieldSet = Fieldset('Forældres oplysninger',
                        Div(
                            Div(Field('name'), css_class="col-md-12"),
                            Div(Field('email'), css_class="col-md-6"),
                            Div(Field('phone'), css_class="col-md-6"),
                            Div(Field('birthday'), css_class="hidden"),
                            css_class="row"
                           )
                     )

        self.helper.layout = Layout(
            nameFieldSet,
            Fieldset('Adresse oplysninger',
                        Div(
                            Div(Field('search_address', id="search-address"), css_class="col-md-10"),
                            Div(Field('manual_entry', id="manual-entry"), css_class="col-md-2"),
                            Div(Field('streetname', readonly=True, css_class="autofilled-address"), css_class="col-md-9"),
                            Div(Field('housenumber', readonly=True, css_class="autofilled-address"), css_class="col-md-1"),
                            Div(Field('floor', readonly=True, css_class="autofilled-address"), css_class="col-md-1"),
                            Div(Field('door', readonly=True, css_class="autofilled-address"), css_class="col-md-1"),
                            Div(Field('zipcode', readonly=True, css_class="autofilled-address"), css_class="col-md-2"),
                            Div(Field('city', readonly=True, css_class="autofilled-address"), css_class="col-md-5"),
                            Div(Field('placename', readonly=True, css_class="autofilled-address"), css_class="col-md-5"),
                            Hidden('dawa_id', '',  id="id_dawa_id"),
                            css_class="row"
                           )
                     ),
            ButtonHolder(
                Submit('submit', 'Opret' if self.instance.id == None else 'Ret', css_class="btn-success"),
                #HTML("""<a class="btn btn-link" href="{% url 'family_detail' family.unique %}">Fortryd</a>""")
            )
        )
        self.helper.render_unmentioned_fields = False
        self.fields['birthday'].input_formats=(settings.DATE_INPUT_FORMATS)
    class Meta:
        model=Person
        fields= ['birthday', 'name','zipcode','city', 'streetname', 'housenumber', 'floor', 'door', 'placename', 'email','phone']

    search_address = forms.CharField(label='Indtast adresse', required=False, max_length=200)
    dawa_id = forms.CharField(label='Dawa ID', max_length=10, widget=forms.HiddenInput(), required=False)
    manual_entry = forms.ChoiceField(label="Indtast felter manuelt", widget=forms.CheckboxInput, required=False, choices=((True, 'True'), (False, 'False')))

class getLoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(getLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-getLoginForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'entry_page'
        self.helper.help_text_inline = False
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Hidden('form_id', 'getlogin',  id="id_form_id"),
            'email',
            ButtonHolder(Submit('submit','Send',css_class='btn btn-primary')),
            )

    email = forms.EmailField(required=True, label="Email", initial="din@email.dk", help_text="Indtast den email adresse du oprindeligt opskrev dig med.", error_messages={'required': 'Indtast din email adresse først', 'invalid' : 'Ikke en gyldig email adresse!'})

class signupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(signupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'entry_page'
        self.helper.html5_required = True
        self.fields['child_birthday'].widget.format = '%d-%m-%Y'
        self.helper.layout = Layout(
            Hidden('form_id', 'signup',  id="id_form_id"),
            Fieldset('Barnets oplysninger',
                        Div(
                             Div(Field('child_name'), css_class="col-md-12"),
                             Div(Field('child_email'), css_class="col-md-6"),
                             Div(Field('child_phone'), css_class="col-md-6"),
                             Div(Field('child_birthday', css_class="datepicker", input_formats=(settings.DATE_INPUT_FORMATS)), css_class="col-md-6"),
                             css_class="row"
                           )
                    ),
            Fieldset('Forældres oplysninger',
                        Div(
                            Div(Field('parent_name'), css_class="col-md-12"),
                            Div(Field('parent_email'), css_class="col-md-6"),
                            Div(Field('parent_phone'), css_class="col-md-6"),
                            css_class="row"
                           )
                     ),
            Fieldset('Adresse oplysninger',
                        Div(
                            Div(Field('search_address', id="search-address"), css_class="col-md-10"),
                            Div(Field('manual_entry', id="manual-entry"), css_class="col-md-2"),
                            Div(Field('streetname', readonly=True, css_class="autofilled-address"), css_class="col-md-9"),
                            Div(Field('housenumber', readonly=True, css_class="autofilled-address"), css_class="col-md-1"),
                            Div(Field('floor', readonly=True, css_class="autofilled-address"), css_class="col-md-1"),
                            Div(Field('door', readonly=True, css_class="autofilled-address"), css_class="col-md-1"),
                            Div(Field('zipcode', readonly=True, css_class="autofilled-address"), css_class="col-md-2"),
                            Div(Field('city', readonly=True, css_class="autofilled-address"), css_class="col-md-5"),
                            Div(Field('placename', readonly=True, css_class="autofilled-address"), css_class="col-md-5"),
                            Hidden('dawa_id', '',  id="id_dawa_id"),
                            css_class="row"
                           )
                     ),
            ButtonHolder(
                Submit('submit', 'Opret', css_class="btn-success")
            )

        )

    child_name = forms.CharField(label='Barns fulde navn', required=True, max_length=200)
    child_email = forms.EmailField(label='Barns email', required=False)
    child_phone = forms.CharField(label='Barns telefon', required=False, max_length=50)
    child_birthday = forms.DateField(label='Barns fødselsdato', input_formats=['%d-%m-%Y'], error_messages={'required': 'Indtast en gyldig dato. (dd-mm-åååå'})

    parent_name = forms.CharField(label='Forældres navn', required=True, max_length=200)
    parent_email = forms.EmailField(label='Forældres email', required=True)
    parent_phone = forms.CharField(label='Forældres telefon', required=True, max_length=50)

    search_address = forms.CharField(label='Indtast adresse', required=False, max_length=200)
    streetname = forms.CharField(label='Vejnavn', required=True, max_length=200)
    housenumber = forms.CharField(label='Nummer', required=True, max_length=5)
    floor = forms.CharField(label='Etage', required=False,max_length=3)
    door = forms.CharField(label='Dør', required=False,max_length=5)
    placename = forms.CharField(label='Stednavn', required=False,max_length=200)
    zipcode = forms.CharField(label='Postnummer', max_length=4)
    city = forms.CharField(label='By', max_length=200, required=False)
    dawa_id = forms.CharField(label='Dawa ID', max_length=10, widget=forms.HiddenInput(), required=False)
    form_id = forms.CharField(label='Form ID', max_length=10, widget=forms.HiddenInput(), initial='signup')
    manual_entry = forms.ChoiceField(label="Indtast felter manuelt", widget=forms.CheckboxInput, required=False, choices=((True, 'True'), (False, 'False')))
