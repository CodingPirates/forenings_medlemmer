import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from members.models import Email, PayableItem


def verify_request_from_quickpay(request):
    check_sum = hmac.new(
        bytes(settings.QUICKPAY_PRIVATE_KEY, "utf-8"),
        bytes(request.body, "utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return check_sum == request.META["HTTP_QUICKPAY_CHECKSUM_SHA256"]


@csrf_exempt
def QuickPayCallbackNew(request):
    if request.method != "POST" or not verify_request_from_quickpay(request):
        return HttpResponseForbidden("Invalid request")

    data = json.loads(str(request.body, "utf8"))
    if data["accepted"] and data["state"] == "processed":
        payment = PayableItem.get(quick_pay_order_id=data["order_id"])
        payment.processed = True
        payment.accepted = True
        payment.save()
        Email.send_payment_confirmation(payment)

    return HttpResponse("OK")
