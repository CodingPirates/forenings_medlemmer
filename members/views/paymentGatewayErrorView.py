from django.shortcuts import render


def paymentGatewayErrorView(request, unique=None):
    return render(request, 'members/payment_gateway_error.html', {'unique': unique})
