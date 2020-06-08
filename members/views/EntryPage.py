from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from members.forms import signupForm, childForm, adultForm, addressForm
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from members.models.family import Family
from members.models.person import Person


@xframe_options_exempt
def EntryPage(request):
    if request.method == "POST":
        # signup has been filled
        childform = childForm(request.POST)
        adultform = adultForm(request.POST)
        addressform = addressForm(request.POST)
        signup = signupForm(request.POST)
        if (
            signup.is_valid()
            and childform.is_valid()
            and adultform.is_valid()
            and addressform.is_valid()
        ):
            # Check that the family doesn't already exist
            try:
                family = Family.objects.get(
                    email__iexact=adultform.cleaned_data["parent_email"]
                )
                # family was already created - we can't create this family again
                adultForm.add_error(
                    "parent_email",
                    "Denne email adresse er allerede oprettet. Du kan tilføje flere børn på samme forælder, når du er kommet videre! - Log ind ovenfor, for at få adgang.",
                )
                return render(
                    request,
                    "members/entry_page.html",
                    {
                        "signupform": signup,
                        "childform": childform,
                        "adultform": adultform,
                        "addressform": addressform,
                    },
                )
            except Exception:
                # all is fine - we did not expect any
                pass
            # create new family.
            family = Family.objects.create(email=adultform.cleaned_data["parent_email"])
            family.confirmed_dtm = timezone.now()
            family.save()
            # create parent as user
            user = User.objects.create_user(
                username=adultform.cleaned_data["parent_email"],
                email=adultform.cleaned_data["parent_email"],
            )

            # Check that both passwords are the same
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
                    "members/entry_page.html",
                    {
                        "signupform": signup,
                        "childform": childform,
                        "adultform": adultform,
                        "addressform": addressform,
                    },
                )

            # create parent
            parent = Person.objects.create(
                membertype=Person.PARENT,
                name=adultform.cleaned_data["parent_name"],
                zipcode=addressform.cleaned_data["zipcode"],
                city=addressform.cleaned_data["city"],
                streetname=addressform.cleaned_data["streetname"],
                housenumber=addressform.cleaned_data["housenumber"],
                floor=addressform.cleaned_data["floor"],
                door=addressform.cleaned_data["door"],
                dawa_id=addressform.cleaned_data["dawa_id"],
                placename=addressform.cleaned_data["placename"],
                email=adultform.cleaned_data["parent_email"],
                phone=adultform.cleaned_data["parent_phone"],
                birthday=adultform.cleaned_data["parent_birthday"],
                gender=adultform.cleaned_data["parent_gender"],
                family=family,
                user=user,
            )
            parent.save()

            # create child
            child = Person.objects.create(
                membertype=Person.CHILD,
                name=childform.cleaned_data["child_name"],
                zipcode=addressform.cleaned_data["zipcode"],
                city=addressform.cleaned_data["city"],
                streetname=addressform.cleaned_data["streetname"],
                housenumber=addressform.cleaned_data["housenumber"],
                floor=addressform.cleaned_data["floor"],
                door=addressform.cleaned_data["door"],
                dawa_id=addressform.cleaned_data["dawa_id"],
                placename=addressform.cleaned_data["placename"],
                email=childform.cleaned_data["child_email"],
                phone=childform.cleaned_data["child_phone"],
                birthday=childform.cleaned_data["child_birthday"],
                gender=childform.cleaned_data["child_gender"],
                family=family,
            )
            child.save()

            # redirect to success
            return HttpResponseRedirect(reverse("user_created"))
        else:
            return render(
                request,
                "members/entry_page.html",
                {
                    "signupform": signup,
                    "childform": childform,
                    "adultform": adultform,
                    "addressform": addressform,
                },
            )

    # initial load (if we did not return above)
    signup = signupForm()
    childform = childForm()
    adultform = adultForm()
    addressform = addressForm()
    return render(
        request,
        "members/entry_page.html",
        {
            "signupform": signup,
            "childform": childform,
            "adultform": adultform,
            "addressform": addressform,
        },
    )
