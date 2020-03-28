from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, HTML, Div
from crispy_forms.bootstrap import FormActions

from members.models.activityparticipant import ActivityParticipant
from members.models.payment import Payment


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
                            '<span class="paymentHelp"><p>Vælg <b>ikke</b> "andet er aftalt", med mindre der er en klar aftale med den aktivitets ansvarlige, ellers vil tilmeldingen blive annulleret igen.{% if activity.will_reserve %} Denne betaling vil kun blive reserveret på dit kort. Vi hæver den først endeligt d. 1/1 det år aktiviteten starter for at sikre, at {{ person.name }} er meldt korrekt ind i foreningen i kalenderåret.{% endif %}</p></span>'
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
                css_class="card",
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
            (Payment.CREDITCARD, "Betalingskort / MobilePay"),
            (Payment.OTHER, "Andet er aftalt"),
        ),
    )
