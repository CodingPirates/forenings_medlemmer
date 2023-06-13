from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, HTML, Div
from django.conf import settings
from members.models import Person


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

        self.fields["birthday"].widget = forms.DateInput(
            attrs={"type": "date"}, format="%Y-%m-%d"
        )
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
        labels = {"birthday": "Fødselsdato"}
        error_messages = {"birthday": {"invalid": "Indtast en gyldig dato."}}
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
