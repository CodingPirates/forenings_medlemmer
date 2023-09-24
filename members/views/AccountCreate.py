from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from members.forms import signupForm
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from members.models.family import Family
from members.models.person import Person


@xframe_options_exempt
def AccountCreate(request):
    if request.method == "POST":
        # support redirecting to specific page after signup
        # this uses `next` parameter, similar to https://docs.djangoproject.com/en/4.2/topics/auth/default/#the-login-required-decorator
        next_url = request.POST["next"]

        # figure out which form was filled out.
        if request.POST["form_id"] == "signup":
            # signup has been filled
            signup = signupForm(next_url, request.POST)
            if signup.is_valid():
                # check if passwords match
                if signup.cleaned_data["password1"] != signup.cleaned_data["password2"]:
                    # Passwords dosent match throw an error
                    signup.add_error("password2", "Adgangskoder er ikke ens")
                    return render(
                        request,
                        "members/volunteer_signup.html",
                        {"vol_signupform": signup},
                    )

                # check if family already exists
                # TODO: rewrite this! >>>>
                try:
                    family = Family.objects.get(
                        email__iexact=request.POST["parent_email"]
                    )
                    # family was already created - we can't create this family again
                    signup.add_error(
                        "parent_email",
                        "Denne email adresse er allerede oprettet. Du kan tilføje flere børn på samme forælder, når du er kommet videre! - Log ind ovenfor, for at få adgang.",
                    )
                    return render(
                        request, "members/account_create.html", {"signupform": signup}
                    )
                except Exception:
                    # all is fine - we did not expect any
                    pass
                # TODO: rewrite this! <<<<
                # create new family.
                family = Family.objects.create(
                    email=signup.cleaned_data["parent_email"]
                )
                family.confirmed_at = timezone.now()
                family.save()

                # create parent as user
                user = User.objects.create_user(
                    username=signup.cleaned_data["parent_email"],
                    email=signup.cleaned_data["parent_email"],
                )
                password = signup.cleaned_data["password2"]
                user.set_password(password)
                user.save()

                # create parent
                parent = Person.objects.create(
                    membertype=Person.PARENT,
                    name=signup.cleaned_data["parent_name"],
                    zipcode=signup.cleaned_data["zipcode"],
                    city=signup.cleaned_data["city"],
                    streetname=signup.cleaned_data["streetname"],
                    housenumber=signup.cleaned_data["housenumber"],
                    floor=signup.cleaned_data["floor"],
                    door=signup.cleaned_data["door"],
                    dawa_id=signup.cleaned_data["dawa_id"],
                    placename=signup.cleaned_data["placename"],
                    email=signup.cleaned_data["parent_email"],
                    phone=signup.cleaned_data["parent_phone"],
                    birthday=signup.cleaned_data["parent_birthday"],
                    gender=signup.cleaned_data["parent_gender"],
                    family=family,
                    user=user,
                )
                parent.save()

                # create child
                child = Person.objects.create(
                    membertype=Person.CHILD,
                    name=signup.cleaned_data["child_name"],
                    zipcode=signup.cleaned_data["zipcode"],
                    city=signup.cleaned_data["city"],
                    streetname=signup.cleaned_data["streetname"],
                    housenumber=signup.cleaned_data["housenumber"],
                    floor=signup.cleaned_data["floor"],
                    door=signup.cleaned_data["door"],
                    dawa_id=signup.cleaned_data["dawa_id"],
                    placename=signup.cleaned_data["placename"],
                    email=signup.cleaned_data["child_email"],
                    phone=signup.cleaned_data["child_phone"],
                    birthday=signup.cleaned_data["child_birthday"],
                    gender=signup.cleaned_data["child_gender"],
                    family=family,
                )
                child.save()

                # redirect to success
                if next_url and next_url != "":
                    return HttpResponseRedirect(
                        f"{reverse('user_created')}?next={next_url}"
                    )
                else:
                    return HttpResponseRedirect(reverse("user_created"))
            else:
                return render(
                    request, "members/account_create.html", {"signupform": signup}
                )

    # initial load (if we did not return above)
    signup = (
        signupForm(next_url=request.GET["next"])
        if "next" in request.GET
        else signupForm()
    )
    return render(request, "members/account_create.html", {"signupform": signup})
