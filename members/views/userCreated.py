from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def userCreated(request):
    next_url = request.GET["next"] if "next" in request.GET else None

    return render(request, "members/user_created.html", {"next_url": next_url})
