from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from members.forms import VolEmailForm
from members.models.department import Department


@xframe_options_exempt
def volunteerEmail(request):
    # figure out which form was filled out.
    if request.method == "POST" and request.POST["form_id"] == "vol_email":
        # email form has been filled
        vol_email = VolEmailForm(request.POST)
        if vol_email.is_valid():
            # email to department leader
            department = Department.objects.get(
                name=vol_email.cleaned_data["volunteer_department"]
            )
            department.new_volunteer_email_dep_head(vol_email)
            return HttpResponseRedirect(reverse("vol_email_sent"))
        else:
            return render(
                request,
                "members/volunteer_email.html",
                {"skip_context": True, "VolEmailForm": vol_email},
            )

    # initial load (if we did not return above)
    vol_email = VolEmailForm()
    return render(
        request,
        "members/volunteer_email.html",
        {"skip_context": True, "VolEmailForm": vol_email},
    )
