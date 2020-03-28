import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from members.models.quickpaytransaction import QuickpayTransaction

import hashlib
import hmac


def signQuickpay(base, private_key):
    return hmac.new(private_key, base, hashlib.sha256).hexdigest()


@csrf_exempt
def QuickpayCallback(request):
    checksum = signQuickpay(
        request.body, bytearray(settings.QUICKPAY_PRIVATE_KEY, "ascii")
    )

    # print("comparing checksum: " + request.META['HTTP_QUICKPAY_CHECKSUM_SHA256'] + " (recieved) to: " + checksum + " (calculated)")
    if checksum == request.META["HTTP_QUICKPAY_CHECKSUM_SHA256"]:
        # Request is authenticated

        # JSON decode
        callback = json.loads(str(request.body, "utf8"))

        # We only care about state = processed or new
        if callback["state"] == "processed" or callback["state"] == "new":
            quickpay_transaction = get_object_or_404(
                QuickpayTransaction, order_id=callback["order_id"]
            )

            if callback["accepted"] and callback["state"] == "processed":
                quickpay_transaction.payment.set_confirmed()
            if callback["accepted"] is False and callback["state"] == "processed":
                quickpay_transaction.payment.set_rejected(request.body)
            if callback["accepted"] and callback["state"] == "new":
                quickpay_transaction.payment.set_accepted()

        return HttpResponse("OK")
    else:
        # Request is Not authenticated
        return HttpResponseForbidden("Invalid request")
