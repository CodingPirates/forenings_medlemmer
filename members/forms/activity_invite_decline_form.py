from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML


class ActivivtyInviteDeclineForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ActivivtyInviteDeclineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Submit("submit", "Afslå invitationen", css_class="button-danger"),
            HTML('<a class="button" href="{% url "activities" %}">Tilbage</a>'),
        )
