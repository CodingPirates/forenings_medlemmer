from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from members.utils.user import has_user, user_to_person


@login_required
@user_passes_test(has_user, "/admin_signup/")
def paymentGatewayErrorView(request):
    unique = user_to_person(request.user).family.unique
    return render(request, "members/payment_gateway_error.html", {"unique": unique})
