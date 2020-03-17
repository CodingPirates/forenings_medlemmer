from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

from members.utils.user import user_to_person, has_user
from members.models import Person, Union, Membership
from members.forms import MembershipForm


@login_required
@user_passes_test(has_user, "/admin_signup/")
def MembershipView(request):
    family = user_to_person(request.user).family
    family_members = Person.objects.filter(family=family)
    unions = Union.objects.all()
    current_memberships = Membership.objects.filter(person__in=family_members).order_by(
        "person", "sign_up_date", "union"
    )
    if request.method == "GET":
        form = MembershipForm(family_members)
        return render(
            request,
            "members/membership_view.html",
            {
                # TODO check for closed unions:
                "unions": unions,
                "family_members": family_members,
                "current_memberships": current_memberships,
                "form": form,
            },
        )
    elif request.method == "POST":
        print(request.POST)
        form = MembershipForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse("membership_view"))
