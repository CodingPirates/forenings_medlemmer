from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from members.forms import adminSignupForm
from members.models.family import Family
from members.models.person import Person
from members.models.volunteer import Volunteer
from members.models.department import Department


@login_required
def AdminSignup(request):
    if request.method == "POST":
        # figure out which form was filled out.
        if request.POST["form_id"] == "admin_fam":
            # signup has been filled
            admin_signup = adminSignupForm(request.POST)
            if admin_signup.is_valid():
                # check if family already exists
                try:
                    family = Family.objects.get(
                        email__iexact=request.POST["volunteer_email"]
                    )
                    # family was already created - we can't create this family again
                    admin_signup.add_error(
                        "volunteer_email",
                        "Der opstod en fejl - familien eksisterer, men er ikke knyttet til brugeren. Kontakt os på kontakt@codingpirates.dk.",
                    )
                    return render(
                        request,
                        "members/admin_signup.html",
                        {"adminSignupForm": admin_signup},
                    )
                except:  # noqa: E722
                    # all is fine - we did not expect any
                    pass
                # create new family.
                family = Family.objects.create(
                    email=admin_signup.cleaned_data["volunteer_email"]
                )
                family.confirmed_at = timezone.now()
                family.save()

                # create volunteer
                admin_person = Person.objects.create(
                    membertype=Person.PARENT,
                    name=admin_signup.cleaned_data["volunteer_name"],
                    zipcode=admin_signup.cleaned_data["zipcode"],
                    city=admin_signup.cleaned_data["city"],
                    streetname=admin_signup.cleaned_data["streetname"],
                    housenumber=admin_signup.cleaned_data["housenumber"],
                    floor=admin_signup.cleaned_data["floor"],
                    door=admin_signup.cleaned_data["door"],
                    dawa_id=admin_signup.cleaned_data["dawa_id"],
                    placename=admin_signup.cleaned_data["placename"],
                    email=admin_signup.cleaned_data["volunteer_email"],
                    phone=admin_signup.cleaned_data["volunteer_phone"],
                    birthday=admin_signup.cleaned_data["volunteer_birthday"],
                    gender=admin_signup.cleaned_data["volunteer_gender"],
                    family=family,
                    user=request.user,
                )
                admin_person.save()

                department = Department.objects.get(
                    name=admin_signup.cleaned_data["volunteer_department"]
                )
                vol_obj = Volunteer.objects.create(
                    person=admin_person, department=department
                )
                vol_obj.save()

                return HttpResponseRedirect(reverse("family_detail"))
            else:
                return render(
                    request,
                    "members/admin_signup.html",
                    {"adminSignupForm": admin_signup},
                )

    # initial load (if we did not return above)
    admin_signup = adminSignupForm()
    return render(
        request, "members/admin_signup.html", {"adminSignupForm": admin_signup}
    )
