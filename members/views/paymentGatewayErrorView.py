from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from members.utils.user import user_to_person


@login_required
def paymentGatewayErrorView(request):
    unique = user_to_person(request.user).family.unique
    return render(request, "members/payment_gateway_error.html", {"unique": unique})
