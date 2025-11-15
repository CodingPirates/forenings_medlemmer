from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.mail import send_mail
import os
import random

from django.conf import settings

from members.forms import (
    VolunteerRequestForm,
    LoggedInVolunteerRequestForm,
)
from members.models.department import Department
from members.models.activity import Activity
from members.models.person import Person
from members.models.volunteerrequest import VolunteerRequest
from members.models.volunteerrequestitem import VolunteerRequestItem


@xframe_options_exempt
def volunteerSignup(request):
    # Check if user is logged in
    if request.user.is_authenticated:
        # Simplified logic for authenticated users - just create volunteer request
        if request.method == "POST":
            logged_in_form = LoggedInVolunteerRequestForm(
                user=request.user, data=request.POST
            )
            if logged_in_form.is_valid():
                # Create volunteer request with selected person
                volunteer_request = VolunteerRequest.objects.create(
                    person=logged_in_form.cleaned_data["person"],
                    info_reference=logged_in_form.cleaned_data["info_reference"],
                    info_whishes=logged_in_form.cleaned_data["info_whishes"],
                )

                # Create VolunteerRequestItem records for selected departments
                departments = logged_in_form.cleaned_data.get("departments", [])
                for department in departments:
                    VolunteerRequestItem.objects.create(
                        volunteer_request=volunteer_request, department=department
                    )

                # Create VolunteerRequestItem records for selected activities
                activities = logged_in_form.cleaned_data.get("activities", [])
                for activity in activities:
                    VolunteerRequestItem.objects.create(
                        volunteer_request=volunteer_request,
                        department=activity.department,
                        activity=activity,
                    )

                # Redirect to success page
                return render(
                    request,
                    "members/volunteer_request_success.html",
                    {"name": logged_in_form.cleaned_data["person"].name},
                )
            else:
                return render(
                    request,
                    "members/logged_in_volunteer_request.html",
                    {"logged_in_form": logged_in_form},
                )

        # initial load for authenticated users
        logged_in_form = LoggedInVolunteerRequestForm(user=request.user)

        # Debug information to help troubleshoot
        debug_info = {
            "user_email": request.user.email,
            "user_has_person": hasattr(request.user, "person"),
            "person_count": None,
            "family_email": None,
        }

        # Get some debug info about the user's setup
        try:
            if hasattr(request.user, "person") and request.user.person:
                debug_info["family_email"] = request.user.person.family.email
                debug_info["person_count"] = Person.objects.filter(
                    family=request.user.person.family, deleted_dtm__isnull=True
                ).count()
        except (AttributeError, Person.DoesNotExist):
            pass

        return render(
            request,
            "members/logged_in_volunteer_request.html",
            {"logged_in_form": logged_in_form, "debug_info": debug_info},
        )

    else:
        # Logic for non-authenticated users (new simplified form)
        if request.method == "POST":
            # Two-step flow: initial form POST -> generate/send code and ask for verification
            # subsequent POST with 'verification_code' -> verify and create records
            if "verification_code" in request.POST:
                # Verification step
                entered_code = request.POST.get("verification_code", "").strip()
                session_code = request.session.get("volunteer_verification_code")
                form_data = request.session.get("volunteer_form_data")
                departments_ids = request.session.get("volunteer_form_departments", [])
                activities_ids = request.session.get("volunteer_form_activities", [])

                # Check if the entered code matches either the session code or the env variable code
                env_code = os.getenv("VOLUNTEER_EMAIL_VERIFICATION_CODE")
                is_valid_code = (entered_code == session_code) or (
                    env_code and entered_code == env_code
                )

                if entered_code and is_valid_code:
                    # Create VolunteerRequest from stored form data
                    if not form_data:
                        return render(
                            request,
                            "members/volunteer_request.html",
                            {"volunteer_request_form": VolunteerRequestForm()},
                        )

                    volunteer_request = VolunteerRequest.objects.create(
                        name=form_data.get("name"),
                        email=form_data.get("email"),
                        phone=form_data.get("phone"),
                        age=form_data.get("age") or None,
                        zip=form_data.get("zip"),
                        info_reference=form_data.get("info_reference", ""),
                        info_whishes=form_data.get("info_whishes", ""),
                    )

                    # Create items
                    for dept_id in departments_ids:
                        try:
                            dept = Department.objects.get(pk=dept_id)
                            VolunteerRequestItem.objects.create(
                                volunteer_request=volunteer_request,
                                department=dept,
                            )
                        except Department.DoesNotExist:
                            pass

                    for act_id in activities_ids:
                        try:
                            act = Activity.objects.get(pk=act_id)
                            VolunteerRequestItem.objects.create(
                                volunteer_request=volunteer_request,
                                department=act.department,
                                activity=act,
                            )
                        except Activity.DoesNotExist:
                            pass

                    # Clear session keys
                    for k in [
                        "volunteer_verification_code",
                        "volunteer_form_data",
                        "volunteer_form_departments",
                        "volunteer_form_activities",
                    ]:
                        if k in request.session:
                            del request.session[k]

                    return render(
                        request,
                        "members/volunteer_request_success.html",
                        {"name": volunteer_request.name},
                    )
                else:
                    # Invalid code
                    return render(
                        request,
                        "members/volunteer_email_verification.html",
                        {
                            "email": request.session.get("volunteer_form_data", {}).get(
                                "email", ""
                            ),
                            "error": "Forkert verifikationskode. Prøv igen.",
                        },
                    )

            else:
                # Initial form submission: validate and send code
                volunteer_request_form = VolunteerRequestForm(request.POST)
                if volunteer_request_form.is_valid():
                    cd = volunteer_request_form.cleaned_data
                    # store form data in session until verification
                    request.session["volunteer_form_data"] = {
                        "name": cd.get("name"),
                        "email": cd.get("email"),
                        "phone": cd.get("phone"),
                        "age": cd.get("age"),
                        "zip": cd.get("zip"),
                        "info_reference": cd.get("info_reference"),
                        "info_whishes": cd.get("info_whishes"),
                    }
                    # store selected departments/activities as id lists
                    request.session["volunteer_form_departments"] = [
                        d.id for d in cd.get("departments", [])
                    ]
                    request.session["volunteer_form_activities"] = [
                        a.id for a in cd.get("activities", [])
                    ]

                    # generate code - use environment variable if available, otherwise random
                    if os.getenv("VOLUNTEER_EMAIL_VERIFICATION_CODE"):
                        code = os.getenv("VOLUNTEER_EMAIL_VERIFICATION_CODE")
                    else:
                        code = f"{random.randint(100000, 999999)}"

                    request.session["volunteer_verification_code"] = code

                    # Always send email (in dev environment, emails won't reach destination but that's OK)
                    try:
                        subject = "Bekræft din email - Coding Pirates frivillig"
                        message = f"""Hej {cd.get('name')},

Tak for din interesse i at blive frivillig hos Coding Pirates!

For at bekræfte din email adresse, skal du indtaste følgende verifikationskode: {code}

Hvis du ikke har anmodet om at blive frivillig hos Coding Pirates, kan du ignorere denne email.

Med venlig hilsen,
Coding Pirates Danmark"""
                        from_email = (
                            getattr(settings, "DEFAULT_FROM_EMAIL", None)
                            or "no-reply@codingpirates.dk"
                        )
                        send_mail(
                            subject,
                            message,
                            from_email,
                            [cd.get("email")],
                            fail_silently=False,
                        )
                    except Exception as e:
                        # Log the error but continue - in dev environment emails might fail
                        print(f"Email sending failed: {e}")

                    return render(
                        request,
                        "members/volunteer_email_verification.html",
                        {"email": cd.get("email")},
                    )
                else:
                    return render(
                        request,
                        "members/volunteer_request.html",
                        {"volunteer_request_form": volunteer_request_form},
                    )
        else:
            # Initial load for non-authenticated users
            volunteer_request_form = VolunteerRequestForm()
            return render(
                request,
                "members/volunteer_request.html",
                {"volunteer_request_form": volunteer_request_form},
            )
