from django import forms
from members.models import Person, Union
from members.models import Membership
from datetime import date


class MembershipForm(forms.Form):
    def __init__(self, family_members, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
        self.family_members = family_members
        self.fields["person"].queryset = Person.objects.filter(pk__in=family_members)
        self.fields["person"].initial = 1

        # TODO exclude closed unions and union where is member
        member_of = [
            membership.union
            for membership in Membership.objects.filter(
                person__in=family_members, sign_up_date__year=date.today().year
            )
        ]
        self.fields["union"].queryset = Union.objects.filter(
            closed__isnull=True
        ).exclude(pk__in=member_of)

    person = forms.ModelChoiceField(Person.objects.none())
    union = forms.ModelChoiceField(Union.objects.none(), label="Forening")

    def clean(self):
        Membership.can_be_member_validator(
            self.cleaned_data["person"], self.cleaned_data["union"]
        )
