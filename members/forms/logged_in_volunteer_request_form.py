from django import forms
from crispy_forms.layout import Fieldset, Div, Field

from members.models.person import Person
from members.models.family import Family
from .base_volunteer_request_form import BaseVolunteerRequestForm


class LoggedInVolunteerRequestForm(BaseVolunteerRequestForm):
    """Form for authenticated users to create volunteer requests for family members"""

    # Person selection from family
    person = forms.ModelChoiceField(
        queryset=Person.objects.none(),  # Will be populated in __init__
        label="Vælg person",
        help_text="Vælg den person fra din familie der skal være frivillig",
        empty_label="--- Vælg person ---",
        required=True,
    )

    def __init__(self, user=None, *args, **kwargs):
        super(LoggedInVolunteerRequestForm, self).__init__(*args, **kwargs)

        # Set up the person queryset based on the user's family
        family = None
        if user and user.is_authenticated:
            # Try to get family through user's person record
            try:
                if hasattr(user, "person") and user.person:
                    family = user.person.family
                else:
                    # Try to find person record for this user
                    person = Person.objects.filter(
                        user=user, deleted_dtm__isnull=True
                    ).first()
                    if person:
                        family = person.family
            except (Person.DoesNotExist, AttributeError):
                # If user doesn't have a person record, try to find family by email
                if user.email:
                    try:
                        family = Family.objects.filter(email=user.email).first()
                    except Family.DoesNotExist:
                        pass

        if family:
            persons_queryset = Person.objects.filter(
                family=family, deleted_dtm__isnull=True
            ).order_by("name")

            self.fields["person"].queryset = persons_queryset

            # If no persons found, update help text
            if not persons_queryset.exists():
                self.fields["person"].help_text = (
                    f"Ingen aktive personer fundet i familien '{family.email}'. Kontakt administratoren for at oprette en person."
                )
        else:
            # No family found - show empty queryset but with helpful message
            self.fields["person"].queryset = Person.objects.none()
            self.fields["person"].help_text = (
                "Ingen familie fundet for din brugerkonto. Kontakt administratoren."
            )

        # Setup the layout
        self.setup_layout()

    def get_basic_fieldset(self):
        """Override to include person selection"""
        return Fieldset(
            "Person oplysninger",
            Div(
                Field("person"),
                css_class="col-md-12",
            ),
            "Frivillig oplysninger",
            Div(
                Field("info_reference"),
                css_class="col-md-12",
            ),
            Div(
                Field("info_whishes"),
                css_class="col-md-12",
            ),
        )
