from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, HTML, Div
from crispy_forms.bootstrap import FormActions

from members.models.activityparticipant import ActivityParticipant


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
                        "Tilmeldingsoplysninger",
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
                        FormActions(
                            HTML(
                                '<span class="paymentHelp"><p>{% if activity.will_reserve %} Denne betaling vil kun blive reserveret på dit kort. Vi hæver den først endeligt d. 1/1 det år aktiviteten starter for at sikre, at {{ person.name }} er meldt korrekt ind i foreningen i kalenderåret.{% endif %}</p></span>'
                            ),
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

    note = forms.CharField(
        label="<span style='color:red'><b>Besked til arrangør</b></span> (Særlige hensyn, gener, allergi, medicin etc.)",
        widget=forms.Textarea,
        required=False,
    )
    photo_permission = forms.ChoiceField(
        label="Må Coding Pirates tage og bruge billeder og videoer af dit barn på aktiviteten? (Billederne lægges typisk på vores hjemmeside og Facebook side)",
        initial="Choose",
        required=True,
        choices=(
            (
                "Choose",
                "Vælg om Coding Pirates må tage billeder af mit barn til denne aktivitet",
            ),
            (ActivityParticipant.PHOTO_OK, "Ja, det er OK"),
            (
                ActivityParticipant.PHOTO_NOTOK,
                "Nej, vi vil ikke have I fotograferer mit barn",
            ),
        ),
    )
    read_conditions = forms.ChoiceField(
        label="Har du <a target='_blank' href=https://codingpirates.dk/medlemsbetingelser/>læst</a> og accepterer du vores handelsbetingelser?",
        initial="NO",
        required=True,
        choices=(("YES", "Ja"), ("NO", "Nej")),
    )
