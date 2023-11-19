from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt

from members.forms import vol_signupForm
from members.models.department import Department
from members.models.family import Family
from members.models.person import Person
from members.models.volunteer import Volunteer
from django.contrib.auth.models import User


@xframe_options_exempt
def volunteerSignup(request):
    if request.method == "POST":
        # figure out which form was filled out.
        if request.POST["form_id"] == "vol_signup":
            # signup has been filled
            vol_signup = vol_signupForm(request.POST)
            if vol_signup.is_valid():
                # check if passwords match
                if (
                    vol_signup.cleaned_data["password1"]
                    != vol_signup.cleaned_data["password2"]
                ):
                    # Passwords dosent match throw an error
                    vol_signup.add_error("password2", "Adgangskoder er ikke ens")
                    return render(
                        request,
                        "members/volunteer_signup.html",
                        {"vol_signupform": vol_signup},
                    )

                # check if family already exists
                try:
                    family = Family.objects.get(
                        email__iexact=request.POST["volunteer_email"]
                    )
                    # family was already created - we can't create this family again
                    vol_signup.add_error(
                        "volunteer_email",
                        "Denne email adresse er allerede oprettet. Log ind ovenfor, for at få adgang.",
                    )
                    return render(
                        request,
                        "members/volunteer_signup.html",
                        {"vol_signupform": vol_signup},
                    )
                except:  # noqa: E722
                    # all is fine - we did not expect any
                    pass
                # create new family.
                family = Family.objects.create(
                    email=vol_signup.cleaned_data["volunteer_email"]
                )
                family.confirmed_at = timezone.now()
                family.save()

                # create volunteer as user
                user = User.objects.create_user(
                    username=vol_signup.cleaned_data["volunteer_email"],
                    email=vol_signup.cleaned_data["volunteer_email"],
                )
                password = vol_signup.cleaned_data["password2"]
                user.set_password(password)
                user.save()

                # create volunteer
                volunteer = Person.objects.create(
                    membertype=Person.PARENT,
                    name=vol_signup.cleaned_data["volunteer_name"],
                    zipcode=vol_signup.cleaned_data["zipcode"],
                    city=vol_signup.cleaned_data["city"],
                    streetname=vol_signup.cleaned_data["streetname"],
                    housenumber=vol_signup.cleaned_data["housenumber"],
                    floor=vol_signup.cleaned_data["floor"],
                    door=vol_signup.cleaned_data["door"],
                    dawa_id=vol_signup.cleaned_data["dawa_id"],
                    placename=vol_signup.cleaned_data["placename"],
                    email=vol_signup.cleaned_data["volunteer_email"],
                    phone=vol_signup.cleaned_data["volunteer_phone"],
                    birthday=vol_signup.cleaned_data["volunteer_birthday"],
                    gender=vol_signup.cleaned_data["volunteer_gender"],
                    family=family,
                    user=user,
                )
                volunteer.save()

                # send email to department leader
                department = Department.objects.get(
                    name=vol_signup.cleaned_data["volunteer_department"]
                )
                vol_obj = Volunteer.objects.create(
                    person=volunteer, department=department
                )
                vol_obj.save()
                # department.new_volunteer_email(vol_signup.cleaned_data['volunteer_name'])

                # redirect to success
                return HttpResponseRedirect(reverse("user_created"))
            else:
                return render(
                    request,
                    "members/volunteer_signup.html",
                    {"vol_signupform": vol_signup},
                )

    # initial load (if we did not return above)
    vol_signup = vol_signupForm()
    return render(
        request, "members/volunteer_signup.html", {"vol_signupform": vol_signup}
    )
