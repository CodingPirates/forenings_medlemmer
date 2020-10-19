from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from members.forms import PersonForm
from members.models.person import Person
from members.utils.user import has_user, user_to_person
from members.views.UpdatePersonFromForm import UpdatePersonFromForm


@login_required
@user_passes_test(has_user, "/admin_signup/")
def PersonUpdate(request, id):
    person = Person.objects.get(pk=id)
    persons_in_family = Person.objects.filter(
        family=user_to_person(request.user).family
    )
    if person in persons_in_family:
        if request.method == "POST":
            form = PersonForm(request.POST, instance=person)
            if form.is_valid():
                UpdatePersonFromForm(person, form)
                return HttpResponseRedirect(reverse("family_detail"))
        else:
            form = PersonForm(instance=person)
        return render(
            request,
            "members/person_create_or_update.html",
            {"form": form, "person": person},
        )
    else:
        return HttpResponse("Du kan kun redigere en person i din egen familie")
