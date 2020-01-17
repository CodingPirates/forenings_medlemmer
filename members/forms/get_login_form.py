from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Hidden


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
