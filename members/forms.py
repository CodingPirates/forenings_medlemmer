from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from members.models import Person, Payment, ActivityParticipant
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField, Field, Hidden, HTML, Div, Button
from crispy_forms.bootstrap import FormActions

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
                         Div(Field('gender'), css_class="col-md-2"),
                         Div(Field('name'), css_class="col-md-10"),
                         Div(Field('birthday', css_class="datepicker", input_formats=(settings.DATE_INPUT_FORMATS)), css_class="col-md-4"),
                         Div(Field('email'), css_class="col-md-4"),
                         Div(Field('phone'), css_class="col-md-4"),
                         css_class="row"
                       )
                )
            self.fields['birthday'].required = True
        else:
            nameFieldSet = Fieldset('Forældres / Værges oplysninger',
                        Div(
                            Div(Field('gender'), css_class="col-md-2"),
                            Div(Field('name'), css_class="col-md-10"),
                            Div(Field('birthday', css_class="datepicker", input_formats=(settings.DATE_INPUT_FORMATS)), css_class="col-md-4"),
                            Div(Field('email'), css_class="col-md-4"),
                            Div(Field('phone'), css_class="col-md-4"),
                            css_class="row"
                           )
                     )
            self.fields['email'].required = True
            self.fields['phone'].required = True

        self.fields['birthday'].widget.format = '%d-%m-%Y'


        self.helper.layout = Layout(
            nameFieldSet,
            Fieldset('Adresse oplysninger',
                        Div(
                            Div(Field('search_address', id="search-address"), css_class="col-md-10"),
                            Div(Field('manual_entry', id="manual-entry"),
                                Field('address_global', id="address-global"),
                                css_class="col-md-2"),
                            Div(Field('streetname', readonly=True, css_class="autofilled-address"), css_class="col-md-9"),
                            Div(Field('housenumber', readonly=True, css_class="autofilled-address"), css_class="col-md-1"),
                            Div(Field('floor', readonly=True, css_class="autofilled-address"), css_class="col-md-1"),
                            Div(Field('door', readonly=True, css_class="autofilled-address"), css_class="col-md-1"),
                            Div(Field('zipcode', readonly=True, css_class="autofilled-address"), css_class="col-md-2"),
                            Div(Field('city', readonly=True, css_class="autofilled-address"), css_class="col-md-5"),
                            Div(Field('placename', readonly=True, css_class="autofilled-address"), css_class="col-md-5"),
                            Field('dawa_id', '',  id="id_dawa_id"),
                            css_class="row"
                           )
                     ),
            ButtonHolder(
                Submit('submit', 'Opret' if self.instance.id == None else 'Ret', css_class="btn-success"),
                HTML("""<a class="btn btn-link" href="{% url 'family_detail' person.family.unique %}">Fortryd</a>""")
            )
        )
        self.helper.render_unmentioned_fields = False
        self.fields['birthday'].input_formats=(settings.DATE_INPUT_FORMATS)
    class Meta:
        model=Person
        fields= ['birthday', 'gender', 'name','zipcode','city', 'streetname', 'housenumber', 'floor', 'door', 'placename', 'email','phone', 'dawa_id']
        labels = {
            'birthday': 'Fødselsdato (dd-mm-åååå)',
        }
        error_messages = {
            'birthday': {'invalid': 'Indtast en gyldig dato. (dd-mm-åååå)'},
        }
        widgets = {'dawa_id': forms.HiddenInput()}


    search_address = forms.CharField(label='Indtast adresse', required=False, max_length=200)
    manual_entry = forms.ChoiceField(label="Indtast felter manuelt", widget=forms.CheckboxInput, required=False, choices=((True, 'True'), (False, 'False')))
    address_global = forms.ChoiceField(label="Opdater hele familien med denne adresse", widget=forms.CheckboxInput, initial=True, required=False, choices=((True, 'True'), (False, 'False')))

class getLoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(getLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-getLoginForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'entry_page'
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Hidden('form_id', 'getlogin',  id="id_form_id"),
            Field('email', placeholder="din@email.dk (den e-mail adresse, du oprindeligt skrev dig op med.)"),
            Submit('submit','Send',css_class='btn btn-primary'))

    email = forms.EmailField(required=True, label="Email", error_messages={'required': 'Indtast din email adresse først', 'invalid' : 'Ikke en gyldig email adresse!'})

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
                             Div(Field('child_gender'), css_class="col-md-2"),
                             Div(Field('child_name'), css_class="col-md-10"),
                             Div(Field('child_birthday', css_class="datepicker", input_formats=(settings.DATE_INPUT_FORMATS)), css_class="col-md-4"),
                             Div(Field('child_email'), css_class="col-md-4"),
                             Div(Field('child_phone'), css_class="col-md-4"),
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

    child_gender = forms.ChoiceField(label="Køn", required=True, choices=Person.MEMBER_GENDER_CHOICES)
    child_name = forms.CharField(label='Barns fulde navn', required=True, max_length=200)
    child_email = forms.EmailField(label='Barns email', required=False)
    child_phone = forms.CharField(label='Barns telefon', required=False, max_length=50)
    child_birthday = forms.DateField(label='Barns fødselsdato (dd-mm-åååå)', input_formats=(settings.DATE_INPUT_FORMATS), error_messages={'invalid': 'Indtast en gyldig dato. (dd-mm-åååå)'})

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
    dawa_id = forms.CharField(label='Dawa ID', max_length=200, widget=forms.HiddenInput(), required=False)
    form_id = forms.CharField(label='Form ID', max_length=10, widget=forms.HiddenInput(), initial='signup')
    manual_entry = forms.ChoiceField(label="Indtast felter manuelt", widget=forms.CheckboxInput, required=False, choices=((True, 'True'), (False, 'False')))

class ActivitySignupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ActivitySignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Div(Div(HTML("<h2>Tilmelding</h2>"), css_class="panel-heading"),
            Div(
            Div(Div(HTML('''
                <p class="lead">Du tilmelder nu <strong>{{person.name}}</strong> til aktiviteten <strong>{{activity.name}}</strong>.
                Aktiviteten finder sted fra {{ activity.start_date|date:"j. F"}} til {{ activity.end_date|date:"j. F"}} og det koster <strong>{{ price | floatformat:2}} kr</strong> at være med.</p>
                <p class="lead"><em>Tilmeldingen er kun gyldig når der er betalt!</em></p>
                '''),
                css_class="col-md-12"),
                css_class="row"),
            Fieldset('Tilmeldings oplysninger',
                Div(
                    Div(
                        Field('note', aria_describedby="noteHelp"),
                        HTML('<span class="noteHelp"><p>{{activity.instructions|linebreaksbr}}</p></span>'),
                        css_class="col-md-6"),
                    Div(
                        'photo_permission', 'address_permission', 'read_conditions',
                        css_class="col-md-6"),
                    css_class="row"),
            ),
            Fieldset('Betaling',
                'payment_option',
                FormActions(Submit('submit', 'Tilmeld og betal', css_class="btn-success"), HTML("<a href='{% url 'family_detail' family.unique %}'>Tilbage</a>")),
            ),
            css_class="panel-body"),
            css_class="panel panel-success"),
        )

    note = forms.CharField(label='Besked til arrangør', widget=forms.Textarea, required=False)
    photo_permission = forms.ChoiceField(label="Må Coding Pirates tage og bruge billeder af dit barn på aktiviteten? (Billederne lægges typisk på vores hjemmeside og Facebook side)", initial=ActivityParticipant.PHOTO_OK, required=True, choices=((ActivityParticipant.PHOTO_OK, 'Ja, det er OK'),(ActivityParticipant.PHOTO_NOTOK, 'Nej, vi vil ikke have i fotograferer')))
    address_permission = forms.ChoiceField(label="Må vi sætte din email samt telefonnummer på holdlisten, der er synlig for de andre deltagere?", initial='YES', required=True, choices=( ('YES', 'Ja'), ('NO', 'Nej') ))
    read_conditions = forms.ChoiceField(label="Har du <a target='_blank' href=http://codingpirates.dk/coding-pirates-handelsbetingelser/>læst</a> og accepterer du vores handelsbetingelser?", initial='YES', required=True, choices=( ('YES', 'Ja'), ('NO', 'Nej') ))
    payment_option = forms.ChoiceField(label="Vælg betalings metode", required=True, choices=((Payment.CREDITCARD, 'VISA/Dankort'), (Payment.OTHER, 'Andet er aftalt')))

class ActivivtyInviteDeclineForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ActivivtyInviteDeclineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.html5_required = True
        self.helper.layout = Layout(
                                    Submit('submit', 'Afslå invitationen', css_class="btn-danger"),
                                    HTML('<a class="btn btn-link" href="{% url "family_detail" activity_invite.person.family.unique %}">Tilbage</a>')
                                    )
