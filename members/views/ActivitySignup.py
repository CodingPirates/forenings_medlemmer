from django.conf import settings
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test

from members.forms import ActivitySignupForm
from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models.member import Member
from members.models.payment import Payment
from members.models.person import Person
from members.utils.user import user_to_person, has_user


@login_required
@user_passes_test(has_user, "/admin_signup/")
def ActivitySignup(request, activity_id, person_id=None):
    # TODO: is should be possible to view an activity without loggin in
    if person_id is None:
        # View only mode
        view_only_mode = True
    else:
        view_only_mode = False

    activity = get_object_or_404(Activity, pk=activity_id)

    participating = False

    if request.resolver_match.url_name == "activity_view_person":
        view_only_mode = True

    family = user_to_person(request.user).family

    if person_id:
        try:
            person = family.person_set.get(pk=person_id)

            # Check not already signed up
            try:
                participant = ActivityParticipant.objects.get(
                    activity=activity, member__person=person
                )
                # found - we can only allow one - switch to view mode
                participating = True
                view_only_mode = True
            except ActivityParticipant.DoesNotExist:
                participating = False  # this was expected - if not signed up yet

        except Person.DoesNotExist:
            raise Http404("Person not found on family")
    else:
        person = None

    if not activity.open_invite:
        """ Make sure valid not expired invitation to event exists """
        try:
            invitation = ActivityInvite.objects.get(
                activity=activity, person=person, expire_dtm__gte=timezone.now()
            )
        except ActivityInvite.DoesNotExist:
            view_only_mode = True  # not invited - switch to view mode
            invitation = None
    else:
        invitation = None

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

    if request.method == "POST":
        if view_only_mode:
            return HttpResponse(
                "Du kan ikke tilmelde dette event nu. (ikke inviteret / tilmelding lukket / du er allerede tilmeldt eller aktiviteten er fuldt booket)"
            )

        if not (activity.min_age <= person.age_years() <= activity.max_age):
            return HttpResponse(
                "Barnet skal være mellem "
                + str(activity.min_age)
                + " og "
                + str(activity.max_age)
                + " år gammel for at deltage. (Er fødselsdatoen udfyldt korrekt ?)"
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

            # Calculate membership
            membership_start = timezone.datetime(
                year=activity.start_date.year, month=1, day=1
            )
            membership_end = timezone.datetime(
                year=activity.start_date.year, month=12, day=31
            )
            # check if person is member, otherwise make a member
            try:
                member = Member.objects.get(person=person)
            except Member.DoesNotExist:
                member = Member(
                    department=activity.department,
                    person=person,
                    member_since=membership_start,
                    member_until=membership_end,
                )
                member.save()

            # update membership end date
            member.member_until = membership_end
            member.save()

            # Make ActivityParticipant
            participant = ActivityParticipant(
                member=member, activity=activity, note=signup_form.cleaned_data["note"]
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

            return_link_url = reverse(
                "activity_view_person", args=[activity.id, person.id]
            )

            # Make payment if activity costs
            if activity.price_in_dkk is not None and activity.price_in_dkk != 0:
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
                        invite.rejected_dtm = timezone.now()
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
        "price": activity.price_in_dkk,
        "seats_left": activity.seats_left(),
        "signupform": signup_form,
        "signup_closed": signup_closed,
        "view_only_mode": view_only_mode,
        "participating": participating,
        "union": union,
    }
    return render(request, "members/activity_signup.html", context)
