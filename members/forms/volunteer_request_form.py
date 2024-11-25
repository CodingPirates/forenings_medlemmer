from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Hidden, Div, Field, Submit

from members.models.volunteerrequest import VolunteerRequest

from members.models.department import Department
from members.models.person import Person

from django.forms.widgets import CheckboxSelectMultiple
from django.utils.html import format_html


class CustomCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        output = []
        for option in self.choices:
            obj = option[1]
            address = f"{obj.name} ("
            if obj.address.descriptiontext:
                address += f"{obj.address.descriptiontext} "
            if obj.address.streetname:
                address += f"{obj.address.streetname} "
            if obj.address.housenumber:
                address += f"{obj.address.housenumber}, "
            if obj.address.zipcode:
                address += f"{obj.address.zipcode} "
            if obj.address.city:
                address += f"{obj.address.city}"
            address += ")"
            output.append(
                format_html(
                    '<label><input type="checkbox" name="{}" value="{}"> {}</label>',
                    name,
                    option[0],
                    address,
                )
            )
        return format_html("<div>{}</div>", format_html("".join(output)))


class VolunteerRequestForm(forms.ModelForm):
    department_list = forms.ModelMultipleChoiceField(
        queryset=Department.objects.filter(closed_dtm__isnull=True)
        .order_by("id")
        .distinct(),
        widget=CustomCheckboxSelectMultiple(),
        required=True,
        label="Vælg Afdeling(er)x",
    )

    family_member = forms.ModelChoiceField(
        queryset=Person.objects.none(),
        required=False,
        label="Vælg person fra familien",
    )

    class Meta:
        model = VolunteerRequest
        fields = [
            "family_member",
            "name",
            "email",
            "phone",
            "age",
            "zip",
            "info_reference",
            "info_whishes",
            "department_list",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["department_list"].label_from_instance = self.label_from_instance

        if user and user.is_authenticated:
            family = user.person.family
            self.fields["family_member"].queryset = family.person_set.all()
            self.fields["name"].initial = user.person.name
            self.fields["email"].initial = user.email
            self.fields["phone"].initial = user.person.phone
            self.fields["age"].initial = user.person.age_years()
            self.fields["zip"].initial = user.person.zipcode
            self.fields["name"].widget = forms.HiddenInput()
            self.fields["email"].widget = forms.HiddenInput()
            self.fields["phone"].widget = forms.HiddenInput()
            self.fields["age"].widget = forms.HiddenInput()
            self.fields["zip"].widget = forms.HiddenInput()
        else:
            self.fields["family_member"].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Hidden("form_id", "volunteer_requestForm", id="id_form_id"),
            Fieldset(
                "Frivilliges oplysninger",
                Div(
                    Div(Field("family_member"), css_class="col-md-12"),
                    Div(Field("name"), css_class="col-md-12"),
                    Div(Field("email"), css_class="col-md-12"),
                    Div(Field("phone"), css_class="col-md-4"),
                    Div(Field("age"), css_class="col-md-4"),
                    Div(Field("zip"), css_class="col-md-4"),
                    Div(Field("info_reference"), css_class="col-md-12"),
                    Div(Field("info_whishes"), css_class="col-md-12"),
                    Div(Field("department_list"), css_class="col-md-12"),
                    css_class="row",
                ),
            ),
            Submit("submit", "Opret", css_class="btn-success"),
        )

    def label_from_instance(self, obj):
        address = f"{obj.name} [{obj.id}]("
        if obj.address.descriptiontext is not None:
            address += f"{obj.address.descriptiontext} "
        if obj.address.streetname is not None:
            address += f"{obj.address.streetname} "
        if obj.address.housenumber is not None:
            address += f"{obj.address.housenumber}, "
        if obj.address.zipcode is not None:
            address += f"{obj.address.zipcode} "
        if obj.address.city is not None:
            address += f"{obj.address.city}"
        if address is not None:
            address = f"({address})"
        return f"{obj.name} {address}"
