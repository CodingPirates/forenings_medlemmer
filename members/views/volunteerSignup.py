from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt

from members.forms import volunteerForm, addressForm, signupForm
from members.models.department import Department
from members.models.family import Family
from members.models.person import Person
from members.models.volunteer import Volunteer
from django.contrib.auth.models import User


@xframe_options_exempt
def volunteerSignup(request):
    if request.method == "POST":
        # figure out which form was filled out.
        # signup has been filled
        volunteerform = volunteerForm(request.POST)
        addressform = addressForm(request.POST)
        signup = signupForm(request.POST)
        if volunteerform.is_valid() and addressform.is_valid() and signup.is_valid():
            # check if family already exists
            try:
                family = Family.objects.get(
                    email__iexact=volunteerform.cleaned_data["volunteer_email"]
                )
                # family was already created - we can't create this family again
                volunteerform.add_error(
                    "volunteer_email",
                    "Denne email adresse er allerede oprettet. Log ind ovenfor, for at få adgang.",
                )
                return render(
                    request,
                    "members/volunteer_signup.html",
                    {
                        "volunteerform": volunteerform,
                        "addressform": addressform,
                        "signupform": signup,
                    },
                )
            except:  # noqa: E722
                # all is fine - we did not expect any
                pass
            # create new family.
            family = Family.objects.create(
                email=volunteerform.cleaned_data["volunteer_email"]
            )
            family.confirmed_dtm = timezone.now()
            family.save()

            # create volunteer as user
            user = User.objects.create_user(
                username=volunteerform.cleaned_data["volunteer_email"],
                email=volunteerform.cleaned_data["volunteer_email"],
            )

            password1 = signup.cleaned_data["password1"]
            password2 = signup.cleaned_data["password2"]
            if password1 and password2 and password1 == password2:
                user.set_password(password2)
                user.save()
            else:
                signup.add_error(
                    "Udfyld venligst begge kodeords felter, og sørg for at de matcher"
                )
                return render(
                    request,
                    "members/volunteer_signup.html",
                    {
                        "signupform": signup,
                        "volunteerform": volunteerform,
                        "addressform": addressform,
                    },
                )

            # create volunteer
            volunteer = Person.objects.create(
                membertype=Person.PARENT,
                name=volunteerform.cleaned_data["volunteer_name"],
                zipcode=addressform.cleaned_data["zipcode"],
                city=addressform.cleaned_data["city"],
                streetname=addressform.cleaned_data["streetname"],
                housenumber=addressform.cleaned_data["housenumber"],
                floor=addressform.cleaned_data["floor"],
                door=addressform.cleaned_data["door"],
                dawa_id=addressform.cleaned_data["dawa_id"],
                placename=addressform.cleaned_data["placename"],
                email=volunteerform.cleaned_data["volunteer_email"],
                phone=volunteerform.cleaned_data["volunteer_phone"],
                birthday=volunteerform.cleaned_data["volunteer_birthday"],
                gender=volunteerform.cleaned_data["volunteer_gender"],
                family=family,
                user=user,
            )
            volunteer.save()

            # send email to department leader
            department = Department.objects.get(
                name=volunteerform.cleaned_data["volunteer_department"]
            )
            vol_obj = Volunteer.objects.create(person=volunteer, department=department)
            vol_obj.save()
            # department.new_volunteer_email(vol_signup.cleaned_data['volunteer_name'])

            # redirect to success
            return HttpResponseRedirect(reverse("user_created"))
        else:
            return render(
                request,
                "members/volunteer_signup.html",
                {
                    "signupform": signup,
                    "volunteerform": volunteerform,
                    "addressform": addressform,
                },
            )

    # initial load (if we did not return above)
    volunteerform = volunteerForm()
    addressform = addressForm()
    signup = signupForm()
    return render(
        request,
        "members/volunteer_signup.html",
        {
            "signupform": signup,
            "volunteerform": volunteerform,
            "addressform": addressform,
        },
    )
