from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, HTML, Div
from crispy_forms.bootstrap import FormActions
from django.utils.safestring import mark_safe

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
                    Aktiviteten finder sted fra {{ activity.start_date|date:"j. F"}} til {{ activity.end_date|date:"j. F"}} og det koster følgende at være med:</p>
                    <table border="4px">
                      <tr>
                        <th>Beskrivelse</th>
                        <th>Pris</th>
                      </tr>
                      <tr>
                        <td>{{ activity.name }}</td>
                        <td>{{ price | floatformat:2 }} kr.</td>
                      </tr>
                      {% if activity.is_eligable_for_membership and union.new_membership_model_activated_at is not None and union.new_membership_model_activated_at.date <= activity.start_date %}
                        <tr>
                          <td>Medlemskab af Coding Pirates {{ union.name }}</td>
                          <td>{% if membership %}Er allerede medlem{% else %}{{ union.membership_price_in_dkk | floatformat:2 }} kr.{% endif %}</td>
                        </tr>
                      {% endif %}
                      <tr>
                        <td><strong>I alt</strong></td>
                        <td><strong>{{ total_price }} kr.</strong></td>
                      </tr>
                    </table>
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
        label=mark_safe(
            "<span style='color:red'><b>Evt. ekstra information:</b></span> Her kan du informere om evt. særlige behov"
        ),
        widget=forms.Textarea,
        required=False,
    )
    photo_permission = forms.ChoiceField(
        label="Må Coding Pirates tage og bruge billeder og videoer af den tilmeldte person på aktiviteten? (Billederne lægges typisk på vores hjemmeside og Facebook side)",
        initial="Choose",
        required=True,
        choices=(
            (
                "Choose",
                "Må Coding Pirates tage billeder af den tilmeldte person til aktiviteten?",
            ),
            (ActivityParticipant.PHOTO_OK, "Ja, det er OK"),
            (
                ActivityParticipant.PHOTO_NOTOK,
                "Nej, I må ikke fotografere den tilmeldte person",
            ),
        ),
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
        photo_permission = self.cleaned_data.get("photo_permission")

        if read_conditions == "NO":
            self.add_error(
                "read_conditions",
                "For at gå til en Coding Pirates aktivitet skal du acceptere vores betingelser.",
            )

        if photo_permission == "Choose":
            self.add_error(
                "photo_permission", "Du skal vælge om vi må tage billeder eller ej."
            )
