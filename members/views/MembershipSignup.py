from django.conf import settings
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from datetime import datetime

from members.forms import MembershipSignupForm
from members.models.member import Member
from members.models.payment import Payment
from members.models.person import Person
from members.models.union import Union
from members.utils.user import user_to_person


def MembershipSignup(request, union_id, person_id=None):
    if person_id is None:
        view_only_mode = True
    else:
        view_only_mode = False

    union = get_object_or_404(Union, pk=union_id)

    is_member = False

    if request.resolver_match.url_name == "membership_view_person":
        view_only_mode = True

    family = None
    if request.user and not request.user.is_anonymous:
        person = user_to_person(request.user)
        if person:
            family = user_to_person(request.user).family

    family_members = []  # participants from current family
    if family:
        current_year = datetime.now().year
        member_until = (
            datetime.now().date().replace(year=current_year, month=12, day=31)
        )
        family_members = [
            member.person.id
            for member in Member.objects.filter(
                union_id=union.id, person__family=family, member_until=member_until
            )
        ]

    if family and person_id:
        try:
            person = family.person_set.get(pk=person_id)

            # Check not already signed up
            try:
                member_until = datetime.now().date().replace(month=12, day=31)
                member = Member.objects.get(
                    union=union, person=person, member_until=member_until
                )
                # found - we can only allow one - switch to view mode
                is_member = True
                view_only_mode = True
            except Member.DoesNotExist:
                is_member = False  # this was expected - if not signed up yet

        except Person.DoesNotExist:
            raise Http404("Person not found on family")
    else:
        person = None

    # signup_closed should default to False
    signup_closed = False

    if (
        not union.memberships_allowed_at
        or timezone.now().date() < union.memberships_allowed_at
    ):
        signup_closed = True

    if request.method == "POST":
        if view_only_mode:
            return HttpResponse(
                "Du kan ikke tilmelde denne forening nu. Foreningen kan være lukket, eller der kan være andre ting, der gør at man ikke kan tilmelde sig pt."
            )

        signup_form = MembershipSignupForm(request.POST)

        if signup_form.is_valid():
            # Sign up and redirect to payment link or family page

            # Make membership
            member = Member(
                person=person,
                union=union,
                price_in_dkk=union.membership_price_in_dkk,
            )
            member.save()

            return_link_url = reverse(
                "membership_view_person", args=[union.id, person.id]
            )

            # Make payment
            payment = Payment(
                payment_type=Payment.CREDITCARD,
                member=member,
                person=person,
                family=family,
                body_text=timezone.now().strftime("%Y-%m-%d")
                + " Betaling for medlemskab hos Coding Pirates "
                + union.name,
                amount_ore=int(union.membership_price_in_dkk * 100),
            )
            payment.save()

            return_link_url = payment.get_quickpaytransaction().get_link_url(
                return_url=settings.BASE_URL
                + reverse("membership_view_person", args=[union.id, person.id])
            )

            return HttpResponseRedirect(return_link_url)
        # fall through else
    else:
        signup_form = MembershipSignupForm()

    context = {
        "family": family,
        "person": person,
        "price": union.membership_price_in_dkk,
        "signupform": signup_form,
        "signup_closed": signup_closed,
        "view_only_mode": view_only_mode,
        "is_member": is_member,
        "family_members": family_members,
        "union": union,
    }
    return render(request, "members/membership_signup.html", context)
