from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
import os
import random
from datetime import datetime

from members.forms import (
    VolunteerRequestForm,
    LoggedInVolunteerRequestForm,
)
from members.models.department import Department
from members.models.activity import Activity
from members.models.person import Person
from members.models.volunteerrequest import VolunteerRequest
from members.models.volunteerrequestitem import VolunteerRequestItem
from members.models.emailtemplate import EmailTemplate


def ensure_volunteer_request_template():
    """Ensure the VOLUNTEER_REQUEST email template exists"""
    template_id = "VOLUNTEER_REQUEST"

    try:
        template = EmailTemplate.objects.get(idname=template_id)
    except EmailTemplate.DoesNotExist:
        # Create the template if it doesn't exist
        body_html = "<h2>Ny frivillig anmodning</h2>\n"
        body_html += "<p>En ny person har anmodet om at blive frivillig hos Coding Pirates.</p>\n"
        body_html += "\n"
        body_html += "{% if activity %}\n"
        body_html += "<p><strong>Aktivitet:</strong> {{ activity.name }}<br>\n"
        body_html += "<strong>Afdeling:</strong> {{ activity.department.name }}</p>\n"
        body_html += "{% elif department %}\n"
        body_html += "<p><strong>Afdeling:</strong> {{ department.name }}</p>\n"
        body_html += "{% endif %}\n"
        body_html += "\n"
        body_html += '<p>Log venligst ind på <a href="{{ site }}/admin/">administratorsystemet</a> for at se detaljerne og kontakte personen.</p>\n'
        body_html += "\n"
        body_html += "<p>Der er ikke inkluderet personlige oplysninger i denne email af hensyn til privatlivsbeskyttelse.</p>\n"
        body_html += "\n"
        body_html += "<p>Med venlig hilsen,<br>\n"
        body_html += "Coding Pirates Danmark</p>"

        body_text = "Ny frivillig anmodning\n"
        body_text += "\n"
        body_text += (
            "En ny person har anmodet om at blive frivillig hos Coding Pirates.\n"
        )
        body_text += "\n"
        body_text += "{% if activity %}Aktivitet: {{ activity.name }}\n"
        body_text += "Afdeling: {{ activity.department.name }}\n"
        body_text += "{% elif department %}Afdeling: {{ department.name }}\n"
        body_text += "{% endif %}\n"
        body_text += "\n"
        body_text += "Log venligst ind på {{ site }}/admin/ for at se detaljerne og kontakte personen.\n"
        body_text += "\n"
        body_text += "Der er ikke inkluderet personlige oplysninger i denne email af hensyn til privatlivsbeskyttelse.\n"
        body_text += "\n"
        body_text += "Med venlig hilsen,\n"
        body_text += "Coding Pirates Danmark"

        template = EmailTemplate.objects.create(
            idname=template_id,
            name="Ny frivillig anmodning",
            description="Email til afdelingsledere og aktivitetsansvarlige når der kommer en ny frivillig anmodning",
            subject="Coding Pirates. Ny frivillig anmodning - {{ timestamp }}",
            from_address="kontakt@codingpirates.dk",
            body_html=body_html,
            body_text=body_text,
            template_help="Template til notifikation af frivillig anmodning. Tilgængelige variable: activity, department, site, timestamp",
        )

    return template


def ensure_volunteer_verification_template():
    """Ensure the VOLUNTEER_VERIFICATION email template exists"""
    template_id = "VOLUNTEER_VERIFICATION"

    try:
        template = EmailTemplate.objects.get(idname=template_id)
    except EmailTemplate.DoesNotExist:
        # Create the template if it doesn't exist
        body_html = "<h2>Bekræft din email</h2>\n"
        body_html += "<p>Hej {{ name }},</p>\n"
        body_html += "\n"
        body_html += (
            "<p>Tak for din interesse i at blive frivillig hos Coding Pirates!</p>\n"
        )
        body_html += "\n"
        body_html += "<p>For at bekræfte din email adresse, skal du indtaste følgende verifikationskode:</p>\n"
        body_html += "<p><strong>{{ verification_code }}</strong></p>\n"
        body_html += "\n"
        body_html += "<p>Hvis du ikke har anmodet om at blive frivillig hos Coding Pirates, kan du ignorere denne email.</p>\n"
        body_html += "\n"
        body_html += "<p>Med venlig hilsen,<br>\n"
        body_html += "Coding Pirates Danmark</p>"

        body_text = "Hej {{ name }},\n"
        body_text += "\n"
        body_text += "Tak for din interesse i at blive frivillig hos Coding Pirates!\n"
        body_text += "\n"
        body_text += "For at bekræfte din email adresse, skal du indtaste følgende verifikationskode: {{ verification_code }}\n"
        body_text += "\n"
        body_text += "Hvis du ikke har anmodet om at blive frivillig hos Coding Pirates, kan du ignorere denne email.\n"
        body_text += "\n"
        body_text += "Med venlig hilsen,\n"
        body_text += "Coding Pirates Danmark"

        template = EmailTemplate.objects.create(
            idname=template_id,
            name="Email verifikation - Frivillig anmodning",
            description="Email til verifikation af email adresse ved frivillig anmodning",
            subject="Bekræft din email - Coding Pirates frivillig",
            from_address="kontakt@codingpirates.dk",
            body_html=body_html,
            body_text=body_text,
            template_help="Template til email verifikation. Tilgængelige variable: name, verification_code",
        )

    return template


def send_volunteer_notification_emails(volunteer_request, departments, activities):
    """Send notification emails to activity responsible contacts and department leaders using EmailTemplate"""

    # Ensure the email template exists
    template = ensure_volunteer_request_template()

    # Create unique timestamp for this batch of emails
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Send emails for activities
    for activity in activities:
        if activity.responsible_contact:
            try:
                context = {
                    "activity": activity,
                    "department": activity.department,
                    "volunteer_request": volunteer_request,
                    "timestamp": timestamp,
                }

                # Check if responsible_contact is a Person object or email string
                if isinstance(activity.responsible_contact, str):
                    # If it's a string email, try to find a Person with that email first
                    try:
                        person = Person.objects.get(email=activity.responsible_contact)
                        template.makeEmail(
                            [person], context, allow_multiple_emails=True
                        )
                    except Person.DoesNotExist:
                        # No Person found, use the enhanced makeEmail with string email directly
                        template.makeEmail(
                            [activity.responsible_contact],
                            context,
                            allow_multiple_emails=True,
                        )
                else:
                    # If it's already a Person object, use it directly
                    template.makeEmail(
                        [activity.responsible_contact],
                        context,
                        allow_multiple_emails=True,
                    )

            except Exception as e:
                print(f"Failed to send activity notification email: {e}")

    # Send emails for departments
    for department in departments:
        try:
            context = {
                "department": department,
                "volunteer_request": volunteer_request,
                "timestamp": timestamp,
            }

            # Create list of recipients
            recipients = []

            # Add department object to send to department_email
            if department.department_email:
                recipients.append(department)

            # Add department leaders as Person objects
            for leader in department.department_leaders.all():
                if leader.email:
                    recipients.append(leader)

            # Send emails using template
            if recipients:
                template.makeEmail(recipients, context, allow_multiple_emails=True)

        except Exception as e:
            print(f"Failed to send department notification email: {e}")


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

                # Send notification emails to responsible contacts and department leaders
                send_volunteer_notification_emails(
                    volunteer_request, departments, activities
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

                    # Create items and collect them for notification emails
                    departments = []
                    activities = []

                    for dept_id in departments_ids:
                        try:
                            dept = Department.objects.get(pk=dept_id)
                            VolunteerRequestItem.objects.create(
                                volunteer_request=volunteer_request,
                                department=dept,
                            )
                            departments.append(dept)
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
                            activities.append(act)
                        except Activity.DoesNotExist:
                            pass

                    # Send notification emails to responsible contacts and department leaders
                    send_volunteer_notification_emails(
                        volunteer_request, departments, activities
                    )

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

                    # Send verification email using EmailTemplate
                    try:
                        verification_template = ensure_volunteer_verification_template()
                        context = {
                            "name": cd.get("name"),
                            "verification_code": code,
                        }
                        verification_template.makeEmail(
                            [cd.get("email")], context, allow_multiple_emails=True
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
