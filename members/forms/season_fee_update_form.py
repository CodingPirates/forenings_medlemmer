from django import forms


class SeasonFeeUpdateForm(forms.Form):
    season_fee_value = forms.DecimalField(
        label="Nyt sæsonbidrag", decimal_places=2, max_digits=8
    )
    reason = forms.CharField(
        label="Begrundelse for ændring", widget=forms.Textarea, required=True
    )
