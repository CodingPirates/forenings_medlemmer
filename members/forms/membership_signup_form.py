from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from django.utils.safestring import mark_safe


class MembershipSignupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MembershipSignupForm, self).__init__(*args, **kwargs)
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
                    <p class="lead">Du melder nu <strong>{{person.name}}</strong> ind som medlem i Coding Pirates <strong>{{union.name}}</strong>.
                    Medlemsskabet starter i dag og løber til og med d. 31. december {% now "Y" %}. Det koster <strong>{{ price | floatformat:2}} kr</strong> at melde sig ind. Medlemskabet giver adgang til at stemme hos Coding Pirates {{union.name}}{% if union.name != 'Denmark' %} og Coding Pirates Denmark{% endif %}</p>
                    <p class="lead"><em>Medlemskabet er kun gyldig når der er betalt!</em></p>
                    """
                            ),
                            css_class="col-md-12",
                        ),
                        css_class="row",
                    ),
                    Fieldset(
                        "Tilmeldingsoplysninger",
                        Div(
                            Div(
                                "read_conditions",
                                css_class="col-md-6",
                            ),
                            css_class="row",
                        ),
                        FormActions(
                            Submit(
                                "submit",
                                "Tilmeld{% if price > 0 %} og betal{% endif %}",
                                css_class="button-success",
                            ),
                            HTML("<a href='{% url 'family_detail' %}'>Tilbage</a>"),
                        ),
                    ),
                    css_class="card-body",
                ),
                css_class="card",
            )
        )

    read_conditions = forms.ChoiceField(
        label=mark_safe(
            "Har du <a target='_blank' href=https://codingpirates.dk/medlemsbetingelser/>læst</a> og accepterer du vores handelsbetingelser?"
        ),
        initial="NO",
        required=True,
        choices=(("YES", "Ja"), ("NO", "Nej")),
    )

    def clean(self):
        read_conditions = self.cleaned_data.get("read_conditions")

        if read_conditions == "NO":
            self.add_error(
                "read_conditions",
                "For at være medlem af en Coding Pirates forening skal du acceptere vores betingelser.",
            )
