from datetime import date, datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from members.forms import ActivitySignupForm
from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models.member import Member
from members.models.payment import Payment
from members.models.person import Person
from members.models.waitinglist import WaitingList
from members.utils.user import user_to_person

from members.utils.age_check import check_is_person_too_young
from members.utils.age_check import check_is_person_too_old


def ActivitySignup(request, activity_id, person_id=None):
    if person_id is None:
        view_only_mode = True
    else:
        view_only_mode = False

    activity = get_object_or_404(Activity, pk=activity_id)
    union = activity.department.union

    participating = False
    membership = False

    if request.resolver_match.url_name == "activity_view_person":
        view_only_mode = True

    family = None
    if request.user and not request.user.is_anonymous:
        person = user_to_person(request.user)
        if person:
            family = user_to_person(request.user).family

    family_participants = []  # participants from current family
    family_subscriptions = []  # waiting list subscriptions for current family
    family_invites = []  # Invites for current family
    if family:
        family_participants = [
            (act.person.id)
            for act in ActivityParticipant.objects.filter(
                activity_id=activity.id, person__family=family
            )
        ]

        for person in family.get_persons():
            if WaitingList.objects.filter(
                department=activity.department, person=person
            ).exists():
                family_subscriptions.append(person.id)

            if ActivityInvite.objects.filter(
                activity=activity, person=person, expire_dtm__gte=timezone.now()
            ).exists():
                family_invites.append(person.id)

    invitation = None
    if family and person_id:
        try:
            person = family.person_set.get(pk=person_id)

            # Check not already signed up
            try:
                participant = ActivityParticipant.objects.get(
                    activity=activity, person=person
                )
                # found - we can only allow one - switch to view mode
                participating = True
                view_only_mode = True
            except ActivityParticipant.DoesNotExist:
                participating = False  # this was expected - if not signed up yet

            # Check if person is member of the union
            try:
                member = Member.objects.get(
                    union=union,
                    person=person,
                    member_until=date(activity.end_date.year, 12, 31),
                )
                membership = True
            except Member.DoesNotExist:
                membership = False

            """If invitation exists, fetch it"""
            try:
                invitation = ActivityInvite.objects.get(
                    activity=activity, person=person, expire_dtm__gte=timezone.now()
                )
            except ActivityInvite.DoesNotExist:
                if not activity.open_invite:
                    view_only_mode = True  # not invited - switch to view mode

        except Person.DoesNotExist:
            raise Http404("Person not found on family")
    else:
        person = None

    # signup_closed should default to False
    signup_closed = False

    # if activity is closed for signup, you should not be able to sign up
    if activity.signup_closing < timezone.now().date():
        view_only_mode = True  # Activivty closed for signup
        signup_closed = True

    # check if activity is full
    if activity.seats_left() <= 0:
        view_only_mode = True  # activity full
        signup_closed = True

    if invitation is not None:
        price = invitation.price_in_dkk
    else:
        price = activity.price_in_dkk

    # total price if the person is already member or membership is not required
    total_price = price

    if (
        not membership
        and activity.is_eligable_for_membership()
        and union.new_membership_model_activated_at is not None
        and union.new_membership_model_activated_at.date() <= activity.start_date
    ):
        total_price = price + union.membership_price_in_dkk

    if request.method == "POST":
        if view_only_mode:
            return HttpResponse(
                "Du kan ikke tilmelde dette event nu. (ikke inviteret / tilmelding lukket / du er allerede tilmeldt eller aktiviteten er fuldt booket)"
            )

        # check if person is old enough
        if check_is_person_too_young(activity, person):
            return HttpResponse(
                f"Deltageren skal være minimum {activity.min_age} år gammel for at deltage. (Er fødselsdatoen udfyldt korrekt ?)"
            )

        # Check if person is too old
        if check_is_person_too_old(activity, person):
            return HttpResponse(
                f"Deltageren skal være maksimum {activity.max_age} år gammel for at deltage. (Er fødselsdatoen udfyldt korrekt ?)"
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

        signup_form = ActivitySignupForm(request.POST)

        if signup_form.is_valid():
            # Sign up and redirect to payment link or family page

            # Make ActivityParticipant
            participant = ActivityParticipant(
                person=person,
                activity=activity,
                note=signup_form.cleaned_data["note"],
                price_in_dkk=activity.price_in_dkk,
            )

            # Make a new member if it's a member activity
            member = None

            if not membership and activity.is_eligable_for_membership():
                payment = union.membership_price_in_dkk
                if (
                    union.new_membership_model_activated_at is None
                    or union.new_membership_model_activated_at.date()
                    <= activity.start_date
                ):
                    payment = 0

                member = Member(
                    union=union,
                    person=person,
                    price_in_dkk=payment,
                    member_since=(
                        datetime.now()
                        if activity.start_date.year == datetime.now().year
                        else date(activity.end_date.year, 1, 1)
                    ),
                )
                member.save()

            # Make sure people have selected yes or no in photo permission and update photo permission
            if signup_form.cleaned_data["photo_permission"] == "Choose":
                return HttpResponse("Du skal vælge om vi må tage billeder eller ej.")

            participant.photo_permission = signup_form.cleaned_data["photo_permission"]
            participant.save()

            # return user to list of activities where they are participating
            return_link_url = f'{reverse("activities")}#tilmeldte-aktiviteter'

            # Make payment if activity costs
            if price is not None and price > 0:
                payment = Payment(
                    payment_type=Payment.CREDITCARD,
                    activity=activity,
                    activityparticipant=participant,
                    person=person,
                    family=family,
                    member=member,
                    body_text=timezone.now().strftime("%Y-%m-%d")
                    + " Betaling for "
                    + activity.name
                    + " på "
                    + activity.department.name,
                    amount_ore=int(total_price * 100),
                )
                payment.save()

                return_link_url = payment.get_quickpaytransaction().get_link_url(
                    return_url=settings.BASE_URL + return_link_url
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

    else:
        signup_form = ActivitySignupForm()

    context = {
        "activity": activity,
        "family": family,
        "family_invites": family_invites,
        "family_participants": family_participants,
        "family_subscriptions": family_subscriptions,
        "invitation": invitation,
        "membership": membership,
        "participating": participating,
        "person": person,
        "price": price,
        "seats_left": activity.seats_left(),
        "signupform": signup_form,
        "signup_closed": signup_closed,
        "total_price": total_price,
        "view_only_mode": view_only_mode,
        "participating": participating,
        "union": union,
        "view_only_mode": view_only_mode,
    }
    return render(request, "members/activity_signup.html", context)
