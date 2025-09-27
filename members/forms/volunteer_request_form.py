from django import forms
from django.utils import timezone
from django.db.models.functions import Lower
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, Field, Submit, Hidden, HTML

from members.models.volunteerrequest import VolunteerRequest

from members.models import Person, Department, Activity
from members.utils.user import user_to_person

from django.forms.widgets import CheckboxSelectMultiple


class VolunteerRequestForm(forms.ModelForm):
    family_member = forms.ModelChoiceField(
        queryset=Person.objects.none(), required=False, label="Vælg person"
    )
    name = forms.CharField(label="Navn", max_length=200)
    email = forms.EmailField(label="Email", max_length=200)
    phone = forms.CharField(label="Telefon", max_length=50)
    age = forms.IntegerField(label="Alder", min_value=7, max_value=99)
    zip = forms.CharField(label="Postnummer", max_length=4)
    info_reference = forms.CharField(
        label="Reference", widget=forms.Textarea(attrs={"rows": 3}), required=False
    )
    info_whishes = forms.CharField(
        label="Ønsker", widget=forms.Textarea(attrs={"rows": 3}), required=False
    )
    email_token = forms.CharField(widget=forms.HiddenInput(), required=False)
    department_list = forms.ModelMultipleChoiceField(
        queryset=Department.objects.filter(closed_dtm__isnull=True).order_by("name"),
        widget=CheckboxSelectMultiple,
        required=False,
        label="Afdelinger",
    )
    activity_list = forms.ModelMultipleChoiceField(
        queryset=Activity.objects.filter(
            end_date__gte=timezone.now(), activitytype__in=["FORLØB", "ARRANGEMENT"]
        ).order_by("name"),
        widget=CheckboxSelectMultiple,
        required=False,
        label="Aktiviteter",
    )

    class Meta:
        model = VolunteerRequest
        fields = [
            "name",
            "email",
            "phone",
            "age",
            "zip",
            "info_reference",
            "info_whishes",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(VolunteerRequestForm, self).__init__(*args, **kwargs)
        self.fields["department_list"].queryset = Department.objects.filter(
            closed_dtm__isnull=True
        ).order_by("name")

        # Dynamically update labels for department_list to include address information
        self.fields["department_list"].choices = [
            (
                department.id,
                f"Coding Pirates {department.name} ({department.address.streetname} {department.address.housenumber}, {department.address.zipcode} {department.address.city})",
            )
            for department in self.fields["department_list"].queryset
        ]

        self.fields["activity_list"].queryset = Activity.objects.filter(
            end_date__gte=timezone.now(), activitytype__in=["FORLØB", "ARRANGEMENT"]
        ).order_by("name")

        # Dynamically update labels for activity_list to include department information and address for activities
        self.fields["activity_list"].choices = [
            (
                activity.id,
                f"{activity.name} hos Coding Pirates {activity.department.name} ({activity.address.streetname} {activity.address.housenumber}, {activity.address.zipcode} {activity.address.city})",
            )
            for activity in self.fields["activity_list"].queryset
        ]

        if user and user.is_authenticated:
            person = user_to_person(user)
            if person:
                family = person.family
                persons_qs = list(family.person_set.all().order_by(Lower("name")))

                choices_list = [
                    (p.pk, p.name if (getattr(p, "name", None) and p.name.strip()) else f"Person #{p.pk}")
                    for p in persons_qs
                ]
                choices_list.insert(0, ("", "(Vælg person)"))
                qs = Person.objects.filter(pk__in=[p.pk for p in persons_qs])
                self.fields["family_member"].queryset = qs
                self.fields["family_member"].choices = choices_list

                if len(persons_qs) > 1:
                    self.fields["family_member"].widget = forms.Select()
                    self.fields["family_member"].required = True
                    self.fields["family_member"].widget.attrs.update(
                        {
                            "class": "form-select js-no-enhance",
                            "data-no-enhance": "1",
                            "aria-label": "Vælg person",
                        }
                    )
                    self.fields["name"].widget = forms.HiddenInput()
                    self.fields["email"].widget = forms.HiddenInput()
                    self.fields["phone"].widget = forms.HiddenInput()
                    self.fields["age"].widget = forms.HiddenInput()
                    self.fields["zip"].widget = forms.HiddenInput()
                else:
                    only = persons_qs[0] if persons_qs else None
                    self.fields["family_member"].widget = forms.HiddenInput()
                    self.fields["family_member"].required = False
                    if only:
                        self.fields["family_member"].initial = only.pk
                        self.fields["name"].initial = only.name
                        self.fields["phone"].initial = only.phone
                        self.fields["age"].initial = only.age_years()
                        self.fields["zip"].initial = only.zipcode
                        self.fields["email"].initial = only.email
        else:
            self.fields["family_member"].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.layout = Layout(
            Hidden("form_id", "volunteer_request", id="id_form_id"),
            Fieldset(
                "Frivilliges oplysninger",
                Div(
                    Div(Field("family_member"), css_class="col-md-12"),
                    Div(Field("name"), css_class="col-md-6"),
                    Div(Field("email"), css_class="col-md-6"),
                    Div(Field("phone"), css_class="col-md-4"),
                    Div(Field("age"), css_class="col-md-4"),
                    Div(Field("zip"), css_class="col-md-4"),
                    Div(Field("info_reference"), css_class="col-md-12"),
                    Div(Field("info_whishes"), css_class="col-md-12"),
                    Div(
                        HTML(
                            '<input type="text" id="input-search-text" '
                            "onkeyup=\"filter_label('input-search-text', 'form-check-label')\" "
                            'placeholder="Søg efter afdelinger eller aktiviteter..." class="form-control">'
                        ),
                        css_class="col-md-12",
                    ),
                    Div(Field("department_list"), css_class="col-md-12"),
                    Div(Field("activity_list"), css_class="col-md-12"),
                    Div(
                        Field("email_token"),
                        css_class="col-md-12",
                        id="email-token-field",
                    ),
                    css_class="row",
                ),
            ),
            Submit("submit", "Opret", css_class="btn-success"),
        )

    def clean(self):
        cleaned_data = super().clean()
        family_member = cleaned_data.get("family_member")
        if family_member:
            cleaned_data["name"] = family_member.name
            cleaned_data["email"] = family_member.email
            cleaned_data["phone"] = family_member.phone
            cleaned_data["age"] = family_member.age_years()
            cleaned_data["zip"] = family_member.zipcode
        return cleaned_data
