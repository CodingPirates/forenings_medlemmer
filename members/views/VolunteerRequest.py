from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from members.forms import VolunteerRequestForm
from members.models.volunteerrequestdepartment import VolunteerRequestDepartment
from members.models.volunteerrequest import VolunteerRequest
from members.models.emailtemplate import EmailTemplate


def volunteer_request_view(request):
    if request.method == "POST":
        volunteer_request_form = VolunteerRequestForm(request.POST, user=request.user)

        if volunteer_request_form.is_valid():
            family_member = volunteer_request_form.cleaned_data.get("family_member")
            if family_member:
                vol_req_obj = VolunteerRequest.objects.create(
                    person=family_member,
                    name="",
                    email="",
                    phone="",
                    age=None,
                    zip="",
                    info_reference=volunteer_request_form.cleaned_data[
                        "info_reference"
                    ],
                    info_whishes=volunteer_request_form.cleaned_data["info_whishes"],
                )
            else:
                vol_req_obj = volunteer_request_form.save()

            departments = volunteer_request_form.cleaned_data["department_list"]
            for department in departments:
                VolunteerRequestDepartment.objects.create(
                    volunteer_request=vol_req_obj, department=department
                )

                # Send email to each department
                email_template = EmailTemplate.objects.get(idname="NEW_VOLUNTEER")
                context = {
                    "volunteer_request": vol_req_obj,
                    "department": department,
                }
                email_template.makeEmail(department, context)


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
        volunteer_request_form = VolunteerRequestForm(user=request.user)

    return render(
        request,
        "members/volunteer_request.html",
        {
            "volunteer_request_form": volunteer_request_form,
        },
    )
