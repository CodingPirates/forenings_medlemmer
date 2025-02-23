from django.conf import settings
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from members.forms import ActivitySignupForm
from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
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

    participating = False

    if request.resolver_match.url_name == "activity_view_person":
        view_only_mode = True

    family = None
    if request.user and not request.user.is_anonymous:
        person = user_to_person(request.user)
        if person:
            family = user_to_person(request.user).family

    family_participants = []  # participants from current family
    family_subscriptions = []  # waiting list subscriptions for current family
    family_invites = []  # invites from current family
    if family:
        family_participants = [
            (act.person.id)
            for act in ActivityParticipant.objects.filter(
                activity_id=activity.id, person__family=family
            )
        ]

        for person in family.get_persons():
            subscriptions = WaitingList.objects.filter(
                department=activity.department, person=person
            )
            if len(subscriptions) > 0:
                family_subscriptions.append(person.id)

            invitations = ActivityInvite.objects.filter(
                activity=activity, person=person
            )
            if len(invitations) > 0:
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

    # if activity is closed for signup, only invited persons can still join
    if activity.signup_closing < timezone.now().date() and invitation is None:
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
            Person.objects.filter(family=family)
            .exclude(membertype=Person.CHILD)
            .count()
            <= 0
        ):
            return HttpResponse(
                "Barnet skal have en forælder eller værge. Gå tilbage og tilføj en før du tilmelder."
            )

        signup_form = ActivitySignupForm(request.POST)

        if signup_form.is_valid():
            # Sign up and redirect to payment link or family page

            # Make ActivityParticipant
            participant = ActivityParticipant(
                person=person,
                activity=activity,
                note=signup_form.cleaned_data["note"],
            )

            # If conditions not accepted, make error
            if signup_form.cleaned_data["read_conditions"] == "NO":
                return HttpResponse(
                    "For at gå til en Coding Pirates aktivitet skal du acceptere vores betingelser."
                )

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
                    body_text=timezone.now().strftime("%Y-%m-%d")
                    + " Betaling for "
                    + activity.name
                    + " på "
                    + activity.department.name,
                    amount_ore=int(price * 100),
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
        # fall through else
    else:
        signup_form = ActivitySignupForm()

    union = activity.department.union

    context = {
        "family": family,
        "activity": activity,
        "person": person,
        "invitation": invitation,
        "price": price,
        "seats_left": activity.seats_left(),
        "signupform": signup_form,
        "signup_closed": signup_closed,
        "view_only_mode": view_only_mode,
        "participating": participating,
        "family_participants": family_participants,
        "family_subscriptions": family_subscriptions,
        "family_invites": family_invites,
        "union": union,
    }
    return render(request, "members/activity_signup.html", context)
