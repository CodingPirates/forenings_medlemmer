from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def userCreated(request):
    return render(request, "members/user_created.html")
