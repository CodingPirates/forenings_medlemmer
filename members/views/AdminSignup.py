from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from members.forms import addressForm, volunteerForm
from members.models.family import Family
from members.models.person import Person
from members.models.volunteer import Volunteer
from members.models.department import Department


@login_required
def AdminSignup(request):
    if request.method == "POST":
        volunteerform = volunteerForm(request.POST)
        addressform = addressForm(request.POST)

        if volunteerform.is_valid() and addressform.is_valid():
            # check if family already exists
            try:
                family = Family.objects.get(
                    email__iexact=volunteerform.cleaned_data["volunteer_email"]
                )
                # family was already created - we can't create this family again
                volunteerform.add_error(
                    "volunteer_email",
                    "Der opstod en fejl - familien eksisterer, men er ikke knyttet til brugeren. Kontakt os på kontakt@codingpirates.dk.",
                )
                return render(
                    request,
                    "members/admin_signup.html",
                    {"volunteerform": volunteerform, "addressform": addressform},
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

            # create volunteer
            admin_person = Person.objects.create(
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
                user=request.user,
            )
            admin_person.save()

            department = Department.objects.get(
                name=volunteerform.cleaned_data["volunteer_department"]
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
                {"volunteerform": volunteerform, "addressform": addressform},
            )

    # initial load (if we did not return above)
    volunteerform = volunteerForm()
    addressform = addressForm()
    return render(
        request,
        "members/admin_signup.html",
        {"volunteerform": volunteerform, "addressform": addressform},
    )
