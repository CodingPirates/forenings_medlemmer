from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Hidden, Div, Field, Submit

from members.models.volunteerrequest import VolunteerRequest

from members.models.department import Department

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
            "department_list",
        ]

    def __init__(self, *args, **kwargs):
        print("INIT")
        super(VolunteerRequestForm, self).__init__(*args, **kwargs)
        self.fields["department_list"].label_from_instance = self.label_from_instance
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Hidden("form_id", "volunteer_requestForm", id="id_form_id"),
            Fieldset(
                "Frivilliges oplysninger",
                Div(
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
