from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from members.forms import VolunteerRequestForm
from members.models.volunteerrequestdepartment import VolunteerRequestDepartment


def volunteer_request_view(request):
    if request.method == "POST":
        volunteer_request_form = VolunteerRequestForm(request.POST)

        if volunteer_request_form.is_valid():
            vol_req_obj = volunteer_request_form.save()
            departments = volunteer_request_form.cleaned_data["department_list"]
            for department in departments:
                VolunteerRequestDepartment.objects.create(
                    volunteer_request=vol_req_obj, department=department
                )

            messages.success(
                request, "Your volunteer request has been submitted successfully!"
            )
            return HttpResponseRedirect(reverse("volunteer_request_created"))
        else:
            return render(
                request,
                "members/volunteer_request.html",
                {
                    "volunteer_request_form": volunteer_request_form,
                },
            )
    else:
        volunteer_request_form = VolunteerRequestForm()

    return render(
        request,
        "members/volunteer_request.html",
        {
            "volunteer_request_form": volunteer_request_form,
        },
    )
