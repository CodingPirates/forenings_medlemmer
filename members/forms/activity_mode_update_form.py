from django import forms
from members.models.activitymode import ActivityMode


class ActivityModeUpdateForm(forms.Form):
    activity_mode = forms.ModelChoiceField(
        queryset=ActivityMode.objects.all(), label="Ny aktivitetsform", required=True
    )
