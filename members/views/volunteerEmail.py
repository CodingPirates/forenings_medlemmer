from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from members.forms import vol_emailForm
from members.models.department import Department


@xframe_options_exempt
def volunteerEmail(request):
    if request.method == "POST":
        # figure out which form was filled out.
        if request.POST["form_id"] == "vol_email":
            # email form has been filled
            vol_email = vol_emailForm(request.POST)
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
                    {"skip_context": True, "vol_emailform": vol_email},
                )

    # initial load (if we did not return above)
    vol_email = vol_emailForm()
    return render(
        request,
        "members/volunteer_email.html",
        {"skip_context": True, "vol_emailform": vol_email},
    )
