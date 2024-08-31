from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from members.forms import MembershipSignupForm
from members.models.member import Member
from members.models.payment import Payment
from members.models.person import Person
from members.models.union import Union
from members.models.waitinglist import WaitingList
from members.utils.user import user_to_person


def MembershipSignup(request, union_id, person_id=None):
    if person_id is None:
        view_only_mode = True
    else:
        view_only_mode = False

    union = get_object_or_404(Union, pk=union_id)

    participating = False

    if request.resolver_match.url_name == "membership_view_person":
        view_only_mode = True

    family = None
    if request.user and not request.user.is_anonymous:
        person = user_to_person(request.user)
        if person:
            family = user_to_person(request.user).family

    family_members = []  # participants from current family
    if family:
        family_members = [
            (member.person.id)
            for member in Member.objects.filter(
                union_id=union.id, person__family=family
            )
        ]

    if family and person_id:
        try:
            person = family.person_set.get(pk=person_id)

            # Check not already signed up
            try:
                member = Member.objects.get(union=union, person=person)
                # found - we can only allow one - switch to view mode
                participating = True
                view_only_mode = True
            except Member.DoesNotExist:
                participating = False  # this was expected - if not signed up yet

        except Person.DoesNotExist:
            raise Http404("Person not found on family")
    else:
        person = None

    # signup_closed should default to False
    signup_closed = False

    if not union.memberships_allowed_at or union.memberships_allowed_at < timezone.now().date():
        signup_closed = True

    if request.method == "POST":
        if view_only_mode:
            return HttpResponse(
                "Du kan ikke tilmelde denne forening nu. Foreningen kan være lukket, eller der kan være andre ting, der gør at man ikke kan tilmelde sig pt."
            )

        if (
            not Person.objects.filter(family=family)
            .exclude(membertype=Person.CHILD)
            .exists()
        ):
            raise ValidationError(
                "Barnet skal have en forælder eller værge. Gå tilbage og tilføj en før du tilmelder.",
                code="no_parent_guardian",
            )

        signup_form = MembershipSignupForm(request.POST)

        if signup_form.is_valid():
            # Sign up and redirect to payment link or family page

            # Make ActivityParticipant
            participant = ActivityParticipant(
                person=person,
                activity=activity,
                note=signup_form.cleaned_data["note"],
                price_in_dkk=activity.price_in_dkk - union.membership_price_in_dkk,
            )

            # Make a new member if it's a member activity
            if activity.is_eligable_for_membership():
                Member(
                    union=union,
                    person=person,
                    price_in_dkk=union.membership_price_in_dkk,
                )

            # Make sure people have selected yes or no in photo permission and update photo permission
            if signup_form.cleaned_data["photo_permission"] == "Choose":
                return HttpResponse("Du skal vælge om vi må tage billeder eller ej.")
            participant.photo_permission = signup_form.cleaned_data["photo_permission"]
            participant.save()

            return_link_url = reverse(
                "activity_view_person", args=[activity.id, person.id]
            )

            # Make payment if activity costs
            if activity.price_in_dkk is not None and activity.price_in_dkk > 0:
                # using creditcard ?
                if signup_form.cleaned_data["payment_option"] == Payment.CREDITCARD:
                    payment = Payment(
                        payment_type=Payment.CREDITCARD,
                        activity=activity,
                        activityparticipant=participant,
                        person=person,
                        family=family,
                        body_text=timezone.now().strftime("%Y-%m-%d")
                        + " Betaling for "
                        + activity.name
                        + " på "
                        + activity.department.name,
                        amount_ore=int(activity.price_in_dkk * 100),
                    )
                    payment.save()

                    return_link_url = payment.get_quickpaytransaction().get_link_url(
                        return_url=settings.BASE_URL
                        + reverse("activity_view_person", args=[activity.id, person.id])
                    )

            # expire invitation
            if invitation:
                invitation.expire_dtm = timezone.now() - timezone.timedelta(days=1)
                invitation.save()

            # reject all seasonal invitations on person if this was a seasonal invite
            # (to avoid signups on multiple departments for club season)
            if activity.is_season():
                invites = ActivityInvite.objects.filter(person=person).exclude(
                    activity=activity
                )
                for invite in invites:
                    if invite.activity.is_season():
                        invite.rejected_at = timezone.now()
                        invite.save()

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
        "participating": participating,
        "family_members": family_members,
        "union": union,
    }
    return render(request, "members/membership_signup.html", context)
