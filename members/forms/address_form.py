from django import forms


class addressForm(forms.Form):
    search_address = forms.CharField(
        label="Indtast adresse", required=False, max_length=200
    )
    streetname = forms.CharField(
        label="Vejnavn",
        required=True,
        max_length=200,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    housenumber = forms.CharField(
        label="Nummer",
        required=True,
        max_length=5,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    floor = forms.CharField(
        label="Etage",
        required=False,
        max_length=3,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    door = forms.CharField(
        label="Dør",
        required=False,
        max_length=5,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    placename = forms.CharField(
        label="Stednavn",
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    zipcode = forms.CharField(
        label="Postnummer",
        max_length=4.0,
        required=True,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    city = forms.CharField(
        label="By",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
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
