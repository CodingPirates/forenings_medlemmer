from django import forms


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
