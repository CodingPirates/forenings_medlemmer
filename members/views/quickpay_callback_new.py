from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from members.models import PayableItem


@csrf_exempt
def QuickPayCallbackNew(request):
    PayableItem.send_all_payment_confirmations()
    return HttpResponse("OK")
