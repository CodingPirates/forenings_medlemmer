from django import forms
from members.models import Person, Union
from datetime import date


class MembershipForm(forms.Form):
    def __init__(self, person_id, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
        self.fields["person"].queryset = Person.objects.filter(pk__in=person_id)
        self.fields["person"].initial = 1

        # TODO exclude closed unions and union where is member
        self.fields["union"].queryset = Union.objects.all()

    person = forms.ModelChoiceField(Person.objects.none())
    union = forms.ModelChoiceField(Union.objects.none())
