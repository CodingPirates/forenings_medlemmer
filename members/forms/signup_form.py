from django import forms
import django.contrib.auth.password_validation as validators


class signupForm(forms.Form):
    password1 = forms.CharField(
        label="Kodeord", required=True, widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Gentag kodeord", required=True, widget=forms.PasswordInput
    )
    form_id = forms.CharField(
        label="Form ID", max_length=10, widget=forms.HiddenInput(), initial="signup"
    )

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        try:
            validators.validate_password(password1)
        except forms.ValidationError as error:
            # Method inherited from BaseForm
            self.add_error("password1", error)
        return password1
