from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from members.forms import MembershipForm
from members.models import Membership, PayableItem, Person, Union
from members.utils.user import has_user, user_to_person


@login_required
@user_passes_test(has_user, "/admin_signup/")
def MembershipView(request):

    logged_in_person = user_to_person(request.user)
    family_members = Person.objects.filter(family=logged_in_person.family)
    unions = Union.objects.filter(closed__isNull=True)
    current_memberships = Membership.objects.filter(person__in=family_members).order_by(
        "person", "sign_up_date", "union"
    )
    if request.method == "GET":
        form = MembershipForm(family_members)
        return render(
            request,
            "members/memberships.html",
            {
                "unions": unions,
                "family_members": family_members,
                "current_memberships": current_memberships,
                "form": form,
            },
        )
    elif request.method == "POST":
        form = MembershipForm(family_members, request.POST)
        if form.is_valid():
            membership = Membership.objects.create(
                person=form.cleaned_data["person"], union=form.cleaned_data["union"]
            )
            payment = PayableItem.objects.create(
                person=logged_in_person,
                amount_ore=membership.union.membership_price_ore,
                membership=membership,
            )
            base_url = "/".join(request.build_absolute_uri().split("/")[:3])
            return HttpResponseRedirect(
                payment.get_link(base_url=base_url, continue_page="payments")
            )
        else:
            return render(
                request,
                "members/memberships.html",
                {
                    "unions": unions,
                    "family_members": family_members,
                    "current_memberships": current_memberships,
                    "form": form,
                },
            )
