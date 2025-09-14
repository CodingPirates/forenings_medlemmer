from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from members.forms import VolunteerRequestForm
from members.models.volunteerrequestdepartment import VolunteerRequestDepartment
from members.models.volunteerrequest import VolunteerRequest
from members.models.emailtemplate import EmailTemplate
from members.forms.signup_form import signupForm
from members.utils.user import user_to_person
import random
import json


def create_user_view(request, token):
    volunteer_request = get_object_or_404(VolunteerRequest, token=token)

    if request.method == "POST":
        form = signupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=volunteer_request.email,
                email=volunteer_request.email,
                password=form.cleaned_data["password1"],
            )
            person = form.save(commit=False)
            person.user = user
            person.save()
            volunteer_request.person = person
            volunteer_request.save()
            return redirect("user_created")
    else:
        form = signupForm(
            initial={
                "parent_name": volunteer_request.name,
                "parent_email": volunteer_request.email,
                "parent_phone": volunteer_request.phone,
                "zipcode": volunteer_request.zip,
            }
        )

    return render(request, "members/create_user.html", {"form": form})


def generate_code(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            if email:
                token = str(random.randint(100000, 999999))
                request.session["email_token"] = token

                email_template = EmailTemplate.objects.get(idname="SECURITY_TOKEN")
                context = {"token": token}
                email_items = email_template.makeEmail([email], context, True)
                for email_item in email_items:
                    email_item.send()  # Send the email immediately

                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "Email is required."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method."})


def volunteer_request(request):
    if request.user.is_authenticated:
        person = user_to_person(request.user)
        if not person:
            return redirect(
                "family_detail"
            )  # Redirect to the "Familie" page if no person record

    if request.method == "POST":
        volunteer_request_form = VolunteerRequestForm(request.POST, user=request.user)

        if volunteer_request_form.is_valid():
            if not request.user.is_authenticated:
                email = volunteer_request_form.cleaned_data["email"]
                email_token = volunteer_request_form.cleaned_data["email_token"]
                session_token = request.session.get("email_token")

                if not session_token:
                    # Generate and send the email token
                    token = str(random.randint(100000, 999999))
                    request.session["email_token"] = token

                    email_template = EmailTemplate.objects.get(idname="SECURITY_TOKEN")
                    context = {"token": token}
                    email_items = email_template.makeEmail([email], context, True)
                    for email_item in email_items:
                        email_item.send()  # Send the email immediately

                    messages.info(
                        request,
                        "En 6-cifret kode er sendt til din email. Indtast koden for at fortsætte.",
                    )
                    return render(
                        request,
                        "members/volunteer_request.html",
                        {
                            "volunteer_request_form": volunteer_request_form,
                        },
                    )

                if email_token != session_token:
                    messages.error(
                        request, "Den indtastede kode er forkert. Prøv igen."
                    )
                    return render(
                        request,
                        "members/volunteer_request.html",
                        {
                            "volunteer_request_form": volunteer_request_form,
                        },
                    )

            activities = volunteer_request_form.cleaned_data["activity_list"]
            departments = volunteer_request_form.cleaned_data["department_list"]

            if not departments and not activities:
                messages.error(
                    request, "Du skal vælge mindst én afdeling eller aktivitet."
                )
                return render(
                    request,
                    "members/volunteer_request.html",
                    {
                        "volunteer_request_form": volunteer_request_form,
                    },
                )

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

            department_list = []
            for department in departments:
                VolunteerRequestDepartment.objects.create(
                    volunteer_request=vol_req_obj, department=department
                )
                department_list.append(department)

            for activity in activities:
                VolunteerRequestDepartment.objects.create(
                    volunteer_request=vol_req_obj,
                    activity=activity,
                    department=activity.department,
                )
                if (
                    activity.department not in department_list
                ):  # If the department is not already in the list
                    department_list.append(activity.department)

            for department in department_list:

                # Send email to each department
                email_template = EmailTemplate.objects.get(idname="NEW_VOLUNTEER")
                context = {
                    "volunteer_request": vol_req_obj,
                    "department": department,
                }
                email_items = email_template.makeEmail(department, context, True)
                for email_item in email_items:
                    email_item.send()  # Send the email immediately

            # Clear the email_token from the session
            if "email_token" in request.session:
                del request.session["email_token"]

            messages.success(
                request, "Your volunteer request has been submitted successfully!"
            )

            if request.user.is_authenticated:
                messages.success(
                    request, "Your volunteer request has been submitted successfully!"
                )
                return redirect("entry_page")

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
