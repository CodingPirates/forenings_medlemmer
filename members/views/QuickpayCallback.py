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

        # We only care about state = processed
        if callback["state"] != "processed":
            HttpResponse("OK")  # processing stops here - but tell QuickPay we are OK

        quickpay_transaction = get_object_or_404(
            QuickpayTransaction, order_id=callback["order_id"]
        )

        if callback["accepted"] is True:
            quickpay_transaction.payment.set_confirmed()
        else:
            quickpay_transaction.payment.set_rejected(request.body)

        return HttpResponse("OK")
    else:
        # Request is Not authenticated
        return HttpResponseForbidden("Invalid request")
