import datetime
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test

from members.utils.user import user_to_person, has_user
from members.models.person import Person
from members.models.activity import Activity
from members.models.activityparticipant import ActivityParticipant
from members.models.payment import Payment
from members.forms import ActivityCancelForm


@login_required
@user_passes_test(has_user, "/admin_signup/")
def RefundActivity(request, activity_id, person_id):
    person = Person.objects.get(pk=person_id)
    activity = Activity.objects.get(pk=activity_id)
    if request.method == "POST":
        form = ActivityCancelForm(request.POST)
        if form.is_valid():
            # mark cancelled, save note and refund
            activityparticipant = ActivityParticipant.objects.get(activity=activity, person=person)
            if not Payment.objects.filter(
                external_id=activityparticipant.payment.external_id,
                status="REFUNDED"
                ).exists():
                payment = Payment(
                    external_id=activityparticipant.payment.external_id,
                    payment_type=Payment.CREDITCARD,
                    person=person,
                    status="REFUNDED",
                    body_text=timezone.now().strftime("%Y-%m-%d")
                    + " Refusion for "
                    + activityparticipant.activity.name
                    + " på "
                    + activityparticipant.activity.department.name,
                    amount_ore=int(activity.price_in_dkk * 100),
                )
                payment.save()
            if activityparticipant.payment.get_quickpaytransaction().refund():
                activityparticipant.removed_dtm = timezone.now()
                activityparticipant.removed_note = form.cleaned_data["cancel_note"]
                activityparticipant.save()
                payment.confirmed_dtm = timezone.now()
                payment.save()
                return HttpResponseRedirect(reverse("payment_refund_success_view"))
            else:
                return HttpResponseRedirect(reverse("payment_refund_error_view"))

    activity_cancel_form = ActivityCancelForm()
    context = {
        "person": person,
        "activity": activity,
        "activity_cancel_form": activity_cancel_form,
    }
    return render(request, "members/refund_activity.html", context)