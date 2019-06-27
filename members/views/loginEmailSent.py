from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def loginEmailSent(request):
    return render(request, "members/login_email_sent.html")
