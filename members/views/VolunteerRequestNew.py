from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt

from members.forms import volunteer_request_new_form
from members.models.department import Department
from members.models.family import Family
from members.models.person import Person
from members.models.volunteer import Volunteer
from members.models.volunteerrequest import VolunteerRequest
from members.models.volunteerrequestdepartment import VolunteerRequestDepartment
from django.contrib.auth.models import User


@xframe_options_exempt
def VolunteerRequestNew(request):
    if request.method == "POST":
        # which form was filled out ?
        if request.POST["form_id"] == "volunteer_request_new_form":
            vol_request_form = volunteer_request_new_form(request.POST)
            if vol_request_form.is_valid():
                #########################################
                # Check for minimum 1 department selected
                #########################################

                # Check if email already exist for a user
                try:
                    family = Family.objects.get(
                        email__iexact=request.POST["volunteer_email"]
                    )
                    vol_request_form.add_error(
                        "volunteer_email",
                        f"Denne email addresse ({family.email}) er allerede oprettet. Log ind ovenfor, for at få adgang.",
                    )
                    # using family.email to ensure family is used, to avoid warning from flake8
                    return render(
                        request,
                        "members/volunteer_request.html",
                        {"volunteer_request_new_form": vol_request_form},
                    )
                except:  # noqa: E722
                    # all is fine - we did not expect any
                    pass

                # Create record for the request
                vol_req_obj = VolunteerRequest.objects.create(
                    person=None,
                    name=vol_request_form.cleaned_data["volunteer_name"],
                    email=None,
                    phone=None,
                    age=None,
                    zip=None,
                    info_reference=None,
                    info_whishes=None,
                    token=None,
                )
                vol_req_obj.save()

                # Loop through all the selected departments and make records for them

                # Send email(s) to department(s) and requestor ?

                return HttpResponseRedirect(reverse("user_created"))  # THIS IS WRONG!
            else:
                return render(
                    request,
                    "members/volunteer_request.html",
                    {"volunteer_request_new_form": vol_request_form},
                )

    # initial load (if we did not return above)
    vol_request_form = volunteer_request_new_form()
    return render(
        request,
        "members/volunteer_request.html",
        {"volunteer_request_new_form": vol_request_form},
    )
