from django import forms
from django.conf import settings
from members.models.activityparticipant import ActivityParticipant
from members.models.department import Department
from members.models.person import Person
from members.models.payment import Payment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Hidden, HTML, Div
from crispy_forms.bootstrap import FormActions


class PersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.html5_required = True
        if self.instance is not None and self.instance.membertype == Person.CHILD:
            nameFieldSet = Fieldset(
                "Barnets oplysninger",
                Div(
                    Div(Field("gender"), css_class="col-md-2"),
                    Div(Field("name"), css_class="col-md-10"),
                    Div(
                        Field(
                            "birthday",
                            css_class="datepicker",
                            input_formats=(settings.DATE_INPUT_FORMATS),
                        ),
                        css_class="col-md-4",
                    ),
                    Div(Field("email"), css_class="col-md-4"),
                    Div(Field("phone"), css_class="col-md-4"),
                    css_class="row",
                ),
            )
            self.fields["birthday"].required = True
            self.fields["gender"].choices = Person.MEMBER_GENDER_CHOICES
        else:
            nameFieldSet = Fieldset(
                "Forældres / Værges oplysninger",
                Div(
                    Div(Field("gender"), css_class="col-md-2"),
                    Div(Field("name"), css_class="col-md-10"),
                    Div(
                        Field(
                            "birthday",
                            css_class="datepicker",
                            input_formats=(settings.DATE_INPUT_FORMATS),
                        ),
                        css_class="col-md-4",
                    ),
                    Div(Field("email"), css_class="col-md-4"),
                    Div(Field("phone"), css_class="col-md-4"),
                    css_class="row",
                ),
            )
            self.fields["email"].required = True
            self.fields["phone"].required = True
            self.fields["gender"].choices = Person.MEMBER_ADULT_GENDER_CHOICES

        self.fields["birthday"].widget.format = "%d-%m-%Y"
        self.fields["streetname"].required = True
        self.fields["housenumber"].required = True
        self.fields["zipcode"].required = True
        self.fields["city"].required = True

        self.helper.layout = Layout(
            nameFieldSet,
            Fieldset(
                "Adresse oplysninger",
                Div(
                    Div(
                        Field("search_address", id="search-address"),
                        css_class="col-md-10",
                    ),
                    Div(
                        Field("manual_entry", id="manual-entry"),
                        Field("address_global", id="address-global"),
                        css_class="col-md-2",
                    ),
                    Div(
                        Field(
                            "streetname", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-9",
                    ),
                    Div(
                        Field(
                            "housenumber", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("floor", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("door", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("zipcode", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-2",
                    ),
                    Div(
                        Field("city", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-5",
                    ),
                    Div(
                        Field(
                            "placename", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-5",
                    ),
                    Field("dawa_id", "", id="id_dawa_id"),
                    css_class="row",
                ),
            ),
            Submit(
                "submit",
                "Opret" if self.instance.id is None else "Ret",
                css_class="btn-success",
            ),
            HTML(
                """<a class="btn btn-link" href="{% url 'family_detail' %}">Fortryd</a>"""
            ),
        )
        self.helper.render_unmentioned_fields = False
        self.fields["birthday"].input_formats = settings.DATE_INPUT_FORMATS

    class Meta:
        model = Person
        fields = [
            "birthday",
            "gender",
            "name",
            "zipcode",
            "city",
            "streetname",
            "housenumber",
            "floor",
            "door",
            "placename",
            "email",
            "phone",
            "dawa_id",
        ]
        labels = {"birthday": "Fødselsdato (dd-mm-åååå)"}
        error_messages = {
            "birthday": {"invalid": "Indtast en gyldig dato. (dd-mm-åååå)"}
        }
        widgets = {"dawa_id": forms.HiddenInput()}

    search_address = forms.CharField(
        label="Indtast adresse", required=False, max_length=200
    )
    manual_entry = forms.ChoiceField(
        label="Indtast felter manuelt",
        widget=forms.CheckboxInput,
        required=False,
        choices=((True, "True"), (False, "False")),
    )
    address_global = forms.ChoiceField(
        label="Opdater hele familien med denne adresse",
        widget=forms.CheckboxInput,
        initial=True,
        required=False,
        choices=((True, "True"), (False, "False")),
    )


class getLoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(getLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-getLoginForm"
        self.helper.form_method = "post"
        self.helper.form_action = "entry_page"
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Hidden("form_id", "getlogin", id="id_form_id"),
            Field(
                "email",
                placeholder="din@email.dk (den e-mail adresse, du oprindeligt skrev dig op med.)",
            ),
            Submit("submit", "Send", css_class="btn btn-primary"),
        )

    email = forms.EmailField(
        required=True,
        label="Email",
        error_messages={
            "required": "Indtast din email adresse først",
            "invalid": "Ikke en gyldig email adresse!",
        },
    )


class signupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(signupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "entry_page"
        self.helper.html5_required = True
        self.fields["child_birthday"].widget.format = "%d-%m-%Y"
        self.helper.layout = Layout(
            Hidden("form_id", "signup", id="id_form_id"),
            Fieldset(
                "Barnets oplysninger",
                Div(
                    Div(Field("child_gender"), css_class="col-md-2"),
                    Div(Field("child_name"), css_class="col-md-10"),
                    Div(
                        Field(
                            "child_birthday",
                            css_class="datepicker",
                            input_formats=(settings.DATE_INPUT_FORMATS),
                        ),
                        css_class="col-md-4",
                    ),
                    Div(Field("child_email"), css_class="col-md-4"),
                    Div(Field("child_phone"), css_class="col-md-4"),
                    css_class="row",
                ),
            ),
            Fieldset(
                "Forældres oplysninger",
                Div(
                    Div(Field("parent_gender"), css_class="col-md-2"),
                    Div(Field("parent_name"), css_class="col-md-10"),
                    Div(
                        Field(
                            "parent_birthday",
                            css_class="datepicker",
                            input_formats=(settings.DATE_INPUT_FORMATS),
                        ),
                        css_class="col-md-4",
                    ),
                    Div(Field("parent_email"), css_class="col-md-4"),
                    Div(Field("parent_phone"), css_class="col-md-4"),
                    css_class="row",
                ),
            ),
            Fieldset(
                "Adresse oplysninger",
                Div(
                    Div(
                        Field("search_address", id="search-address"),
                        css_class="col-md-10",
                    ),
                    Div(Field("manual_entry", id="manual-entry"), css_class="col-md-2"),
                    Div(
                        Field(
                            "streetname", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-9",
                    ),
                    Div(
                        Field(
                            "housenumber", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("floor", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("door", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("zipcode", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-2",
                    ),
                    Div(
                        Field("city", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-5",
                    ),
                    Div(
                        Field(
                            "placename", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-5",
                    ),
                    Hidden("dawa_id", "", id="id_dawa_id"),
                    css_class="row",
                ),
            ),
            Submit("submit", "Opret", css_class="btn-success"),
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
        label="Barns fødselsdato (dd-mm-åååå)",
        input_formats=(settings.DATE_INPUT_FORMATS),
        error_messages={"invalid": "Indtast en gyldig dato. (dd-mm-åååå)"},
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
        label="Forældres fødselsdato (dd-mm-åååå)",
        input_formats=(settings.DATE_INPUT_FORMATS),
        error_messages={"invalid": "Indtast en gyldig dato. (dd-mm-åååå)"},
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


class vol_signupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(vol_signupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "volunteer_signup"
        self.helper.html5_required = True
        self.fields["volunteer_birthday"].widget.format = "%d-%m-%Y"
        self.helper.layout = Layout(
            Hidden("form_id", "vol_signup", id="id_form_id"),
            Fieldset(
                "Frivilliges oplysninger",
                Div(
                    Div(Field("volunteer_gender"), css_class="col-md-2"),
                    Div(Field("volunteer_name"), css_class="col-md-10"),
                    Div(
                        Field(
                            "volunteer_birthday",
                            css_class="datepicker",
                            input_formats=(settings.DATE_INPUT_FORMATS),
                        ),
                        css_class="col-md-3",
                    ),
                    Div(Field("volunteer_email"), css_class="col-md-3"),
                    Div(Field("volunteer_phone"), css_class="col-md-3"),
                    Div(Field("volunteer_department"), css_class="col-md-3"),
                    css_class="row",
                ),
            ),
            Fieldset(
                "Adresse oplysninger",
                Div(
                    Div(
                        Field("search_address", id="search-address"),
                        css_class="col-md-10",
                    ),
                    Div(Field("manual_entry", id="manual-entry"), css_class="col-md-2"),
                    Div(
                        Field(
                            "streetname", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-9",
                    ),
                    Div(
                        Field(
                            "housenumber", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("floor", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("door", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("zipcode", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-2",
                    ),
                    Div(
                        Field("city", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-5",
                    ),
                    Div(
                        Field(
                            "placename", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-5",
                    ),
                    Hidden("dawa_id", "", id="id_dawa_id"),
                    css_class="row",
                ),
            ),
            Submit("submit", "Opret", css_class="btn-success"),
        )

    volunteer_gender = forms.ChoiceField(
        label="Køn", required=True, choices=Person.MEMBER_ADULT_GENDER_CHOICES
    )
    volunteer_name = forms.CharField(label="Fulde navn", required=True, max_length=200)
    volunteer_email = forms.EmailField(label="Email", required=True)
    volunteer_phone = forms.CharField(label="Telefon", required=True, max_length=50)
    volunteer_birthday = forms.DateField(
        label="Fødselsdato (dd-mm-åååå)",
        required=True,
        input_formats=(settings.DATE_INPUT_FORMATS),
        error_messages={"invalid": "Indtast en gyldig dato. (dd-mm-åååå)"},
    )
    volunteer_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        label="Afdeling",
        empty_label="-",
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


class adminSignupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(adminSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "admin_signup"
        self.helper.html5_required = True
        self.fields["volunteer_birthday"].widget.format = "%d-%m-%Y"
        self.helper.layout = Layout(
            Hidden("form_id", "admin_fam", id="id_form_id"),
            Fieldset(
                "Kaptajnens oplysninger",
                Div(
                    Div(Field("volunteer_gender"), css_class="col-md-2"),
                    Div(Field("volunteer_name"), css_class="col-md-10"),
                    Div(
                        Field(
                            "volunteer_birthday",
                            css_class="datepicker",
                            input_formats=(settings.DATE_INPUT_FORMATS),
                        ),
                        css_class="col-md-3",
                    ),
                    Div(Field("volunteer_email"), css_class="col-md-3"),
                    Div(Field("volunteer_phone"), css_class="col-md-3"),
                    Div(Field("volunteer_department"), css_class="col-md-3"),
                    css_class="row",
                ),
            ),
            Fieldset(
                "Adresse oplysninger",
                Div(
                    Div(
                        Field("search_address", id="search-address"),
                        css_class="col-md-10",
                    ),
                    Div(Field("manual_entry", id="manual-entry"), css_class="col-md-2"),
                    Div(
                        Field(
                            "streetname", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-9",
                    ),
                    Div(
                        Field(
                            "housenumber", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("floor", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("door", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-1",
                    ),
                    Div(
                        Field("zipcode", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-2",
                    ),
                    Div(
                        Field("city", readonly=True, css_class="autofilled-address"),
                        css_class="col-md-5",
                    ),
                    Div(
                        Field(
                            "placename", readonly=True, css_class="autofilled-address"
                        ),
                        css_class="col-md-5",
                    ),
                    Hidden("dawa_id", "", id="id_dawa_id"),
                    css_class="row",
                ),
            ),
            Submit("submit", "Opret", css_class="btn-success"),
        )

    volunteer_gender = forms.ChoiceField(
        label="Køn", required=True, choices=Person.MEMBER_ADULT_GENDER_CHOICES
    )
    volunteer_name = forms.CharField(label="Fulde navn", required=True, max_length=200)
    volunteer_email = forms.EmailField(label="Email", required=True)
    volunteer_phone = forms.CharField(label="Telefon", required=True, max_length=50)
    volunteer_birthday = forms.DateField(
        label="Fødselsdato (dd-mm-åååå)",
        required=True,
        input_formats=(settings.DATE_INPUT_FORMATS),
        error_messages={"invalid": "Indtast en gyldig dato. (dd-mm-åååå)"},
    )
    volunteer_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        label="Afdeling",
        empty_label="-",
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


class ActivitySignupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ActivitySignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Div(
                Div(HTML("<h2>Tilmelding</h2>"), css_class="card-header"),
                Div(
                    Div(
                        Div(
                            HTML(
                                """
                    <p class="lead">Du tilmelder nu <strong>{{person.name}}</strong> til aktiviteten {{activity.name}} på <strong>{{activity.department.name}}</strong>.
                    Aktiviteten finder sted fra {{ activity.start_date|date:"j. F"}} til {{ activity.end_date|date:"j. F"}} og det koster <strong>{{ price | floatformat:2}} kr</strong> at være med.</p>
                    <p class="lead"><em>Tilmeldingen er kun gyldig når der er betalt!</em></p>
                    """
                            ),
                            css_class="col-md-12",
                        ),
                        css_class="row",
                    ),
                    Fieldset(
                        "Tilmeldings oplysninger",
                        Div(
                            Div(
                                Field("note", aria_describedby="noteHelp"),
                                HTML(
                                    '<span class="noteHelp"><p>{{activity.instructions|linebreaksbr}}</p></span>'
                                ),
                                css_class="col-md-6",
                            ),
                            Div(
                                "photo_permission",
                                "read_conditions",
                                css_class="col-md-6",
                            ),
                            css_class="row",
                        ),
                    ),
                    Fieldset(
                        "Betaling",
                        Field("payment_option", aria_describedby="paymentHelp"),
                        HTML(
                            '<span class="paymentHelp"><p>Vælg <b>ikke</b> "andet er aftalt", med mindre der er en klar aftale med den aktivitets ansvarlige, ellers vil tilmeldingen blive annulleret igen</p></span>'
                        ),
                        FormActions(
                            Submit(
                                "submit", "Tilmeld og betal", css_class="btn-success"
                            ),
                            HTML("<a href='{% url 'family_detail' %}'>Tilbage</a>"),
                        ),
                    ),
                    css_class="card-body",
                ),
                css_class="card bg-success",
            )
        )

    note = forms.CharField(
        label="Besked til arrangør", widget=forms.Textarea, required=False
    )
    photo_permission = forms.ChoiceField(
        label="Må Coding Pirates tage og bruge billeder og videoer af dit barn på aktiviteten? (Billederne lægges typisk på vores hjemmeside og Facebook side)",
        initial="Choose",
        required=True,
        choices=(
            ("Choose", "Vælg om vi må tage billeder"),
            (ActivityParticipant.PHOTO_OK, "Ja, det er OK"),
            (ActivityParticipant.PHOTO_NOTOK, "Nej, vi vil ikke have i fotograferer"),
        ),
    )
    read_conditions = forms.ChoiceField(
        label="Har du <a target='_blank' href=https://codingpirates.dk/medlemsbetingelser/>læst</a> og accepterer du vores handelsbetingelser?",
        initial="NO",
        required=True,
        choices=(("YES", "Ja"), ("NO", "Nej")),
    )
    payment_option = forms.ChoiceField(
        label="Vælg betalings metode",
        required=True,
        choices=(
            (Payment.CREDITCARD, "Betalingskort / Mobilepay"),
            (Payment.OTHER, "Andet er aftalt"),
        ),
    )


class ActivivtyInviteDeclineForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ActivivtyInviteDeclineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Submit("submit", "Afslå invitationen", css_class="btn-danger"),
            HTML(
                '<a class="btn btn-link" href="{% url "family_detail" %}">Tilbage</a>'
            ),
        )
