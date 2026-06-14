from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from members.models.activityparticipant import ActivityParticipant
from members.utils.user import user_to_person
from members.views.UnacceptedInvitations import get_unaccepted_invitations_for_family


@xframe_options_exempt
def EntryPage(request):
    context = {}
    show_slack_menu = False
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.has_perm(
            "members.can_approve_slack_invites"
        ):
            show_slack_menu = True
    if not request.user.is_anonymous:
        user = user_to_person(request.user)
        if user is None:
            # e.g. if logged in as admin
            context = {"show_slack_menu": show_slack_menu}
        else:
            family = user.family
            unaccepted_invitations = get_unaccepted_invitations_for_family(family)
            missing_payments = ActivityParticipant.get_missing_payments_for_family(
                family
            )

            # Add unpaid membership payments
            from members.models.payment import Payment

            # Show all unpaid payments (no deduplication), skip 0 kr memberships

            unpaid_payments = []
            for payment in Payment.objects.filter(
                family=family,
                confirmed_at__isnull=True,
                accepted_at__isnull=True,
                cancelled_at__isnull=True,
                refunded_at__isnull=True,
                rejected_at__isnull=True,
            ).select_related("member", "person", "member__union", "activity"):
                if payment.member and payment.amount_ore == 0:
                    continue
                payment.amount_dkk = payment.amount_ore / 100.0
                unpaid_payments.append(payment)

            total_missing_ore = sum(p.amount_ore for p in unpaid_payments)
            total_missing_dkk = total_missing_ore / 100.0

            context = {
                "missing_payments": missing_payments,
                "invites": unaccepted_invitations,
                "unpaid_payments": unpaid_payments,
                "total_missing_dkk": total_missing_dkk,
                "show_slack_menu": show_slack_menu,
            }
    else:
        context = {"show_slack_menu": show_slack_menu}

    return render(request, "members/entry_page.html", context)
