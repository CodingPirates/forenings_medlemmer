from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponse


@xframe_options_exempt
def userCreated(request):
    if "password" in request.session:
        password = request.session.get("password")
        del request.session["password"]
    else:
        return HttpResponse(
            "Du kan ikke tilgå adressen direkte. Du skal oprette en bruger for at komme hertil."
        )
    return render(request, "members/user_created.html", {"password": password})
