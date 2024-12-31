from django import forms
from django.utils import timezone
from django.conf import settings
from django.db.models.functions import Lower
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, Field, Submit, Hidden, Div

from members.models.volunteerrequest import VolunteerRequest

# from members.models.department import Department
# from members.models.person import Person
from members.models import Person, Department, Activity  # , Union
from members.models.person import Person

from django.forms.widgets import CheckboxSelectMultiple, CheckboxInput


class VolunteerRequestForm(forms.Form):
    def get_act_dynamic():
        x = [(obj.id, obj.name) for obj in Activity.objects.filter(
            end_date__gte=timezone.now(), activitytype__in=["FORLØB", "ARRANGEMENT"]
        ).order_by("name")]
        print(f"get_act_dyn:{x}")
        return x

    family_member = forms.ModelChoiceField(queryset=Person.objects.none(), required=False, label="Vælg person")
    name = forms.CharField(label="Navn", max_length=200)
    email = forms.EmailField(label="Email", required=True)
    phone = forms.CharField(label="Telefon", max_length=50)
    age = forms.IntegerField(label="Alder")
    zip = forms.CharField(label="Postnummer", max_length=4)
    info_reference = forms.CharField(label="Reference", widget=forms.Textarea(attrs={"rows":3}), required=False)
    info_whishes = forms.CharField(label="Ønsker", widget=forms.Textarea(attrs={"rows":3}), required=False)
    email_token = forms.CharField(widget=forms.HiddenInput(), required=False)
    department_list = forms.ModelMultipleChoiceField(
        queryset=Department.objects.filter(closed_dtm__isnull=True).order_by("name"),
        widget=CheckboxSelectMultiple,
        required=True,
    )
    activity_list = forms.MultipleChoiceField(
        choices=get_act_dynamic,
        widget=CheckboxSelectMultiple, 
        required=False, 
        )
    #activity_list = forms.ChoiceField(choices=get_act_dynamic, widget=forms.RadioSelectMultiple , required=False)
    

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(VolunteerRequestForm, self).__init__(*args, **kwargs)
        self.fields["department_list"].queryset = Department.objects.filter(
            closed_dtm__isnull=True
        ).order_by("name")
        if user and user.is_authenticated:
            family = user.person.family
            self.fields["family_member"].queryset = family.person_set.all().order_by(Lower('name'))
            self.fields["name"].initial = user.person.name
            self.fields["phone"].initial = user.person.phone
            self.fields["age"].initial = user.person.age_years()
            self.fields["zip"].initial = user.person.zipcode
            self.fields["name"].widget = forms.HiddenInput()
            self.fields["email"].widget = forms.HiddenInput()
            self.fields["phone"].widget = forms.HiddenInput()
            self.fields["age"].widget = forms.HiddenInput()
            self.fields["zip"].widget = forms.HiddenInput()
            self.fields["email_token"].widget = forms.HiddenInput()
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
                    Div(Field("name"), css_class="col-md-12"),
                    Div(Field("email"), css_class="col-md-12"),
                    Div(Field("phone"), css_class="col-md-4"),
                    Div(Field("age"), css_class="col-md-4"),
                    Div(Field("zip"), css_class="col-md-4"),
                    Div(Field("info_reference"), css_class="col-md-12"),
                    Div(Field("info_whishes"), css_class="col-md-12"),
                    Div(Field("department_list"), css_class="col-md-12"),
                    Div(Field("activity_list"), css_class="col-md-12"),
                        #css_class="col-md-12",
                        #css_type="checkbox",
                        #type="checkbox",
                        #),
                    Div(Field("email_token"), css_class="col-md-12", id="email-token-field"),
                    css_class="row",
                ),
            ),
            Submit("submit", "Opret", css_class="btn-success"),
        )
