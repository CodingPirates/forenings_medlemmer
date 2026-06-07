from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from members.forms import signupForm
from members.models.family import Family
from members.models.person import Person
from members.models.consent import Consent
from members.models.volunteerrequest import VolunteerRequest
from members.models.volunteerrequestitem import VolunteerRequestItem
from members.models.volunteer import Volunteer


@xframe_options_exempt
def VolunteerAccountCreate(request, token):
    """Create account for volunteer based on token from volunteer request"""

    # Get the volunteer request by token
    volunteer_request = get_object_or_404(VolunteerRequest, token=token)

    # Check if there are any items with status WAITING
    waiting_items = VolunteerRequestItem.objects.filter(
        volunteer_request=volunteer_request, status="WAITING"
    )

    if not waiting_items.exists():
        # No waiting items found
        messages.error(
            request, "Denne anmodning er ikke længere gyldig eller allerede behandlet."
        )
        return render(
            request,
            "members/volunteer_account_error.html",
            {"error": "Anmodning ikke gyldig"},
        )

    if request.method == "POST":
        # Pre-fill form with volunteer request data
        signup = signupForm(next_url="", data=request.POST)
        # Override form action to post back to this volunteer account creation URL
        signup.helper.form_action = f"/account/create/volunteer/{token}/"

        if signup.is_valid():
            # check if passwords match
            if signup.cleaned_data["password1"] != signup.cleaned_data["password2"]:
                signup.add_error("password2", "Adgangskoder er ikke ens")
                return render(
                    request,
                    "members/volunteer_account_create.html",
                    {"signupform": signup, "volunteer_request": volunteer_request},
                )

            # Ensure consent is given
            if not signup.cleaned_data["consent"]:
                signup.add_error(
                    "consent",
                    "Du skal acceptere privatlivspolitikken for at fortsætte.",
                )
                return render(
                    request,
                    "members/volunteer_account_create.html",
                    {"signupform": signup, "volunteer_request": volunteer_request},
                )

            # check if family already exists
            try:
                family = Family.objects.get(
                    email__iexact=signup.cleaned_data["parent_email"]
                )
                # family was already created - we can't create this family again
                signup.add_error(
                    "parent_email",
                    "Denne email adresse er allerede oprettet. Log ind på siden for at få adgang til dit eksisterende medlemskab.",
                )
                return render(
                    request,
                    "members/volunteer_account_create.html",
                    {"signupform": signup, "volunteer_request": volunteer_request},
                )
            except Family.DoesNotExist:
                # all is fine - we did not expect any
                pass

            # Create new family
            family = Family.objects.create(
                email=signup.cleaned_data["parent_email"],
                referer=signup.cleaned_data.get("volunteer_info_reference", ""),
            )
            family.confirmed_at = timezone.now()
            family.save()

            # create user
            user = User.objects.create_user(
                username=signup.cleaned_data["parent_email"],
                email=signup.cleaned_data["parent_email"],
            )
            password = signup.cleaned_data["password2"]
            user.set_password(password)
            user.save()

            # Get the latest consent
            latest_consent = (
                Consent.objects.filter(
                    released_at__isnull=False, released_at__lte=timezone.now()
                )
                .order_by("-released_at")
                .first()
            )

            # create person (volunteer)
            person = Person.objects.create(
                membertype=Person.PARENT,  # Volunteers are typically parents
                name=signup.cleaned_data["parent_name"],
                zipcode=signup.cleaned_data["zipcode"],
                city=signup.cleaned_data["city"],
                streetname=signup.cleaned_data["streetname"],
                housenumber=signup.cleaned_data["housenumber"],
                floor=signup.cleaned_data["floor"],
                door=signup.cleaned_data["door"],
                dawa_id=signup.cleaned_data["dawa_id"],
                placename=signup.cleaned_data["placename"],
                email=signup.cleaned_data["parent_email"],
                phone=signup.cleaned_data["parent_phone"],
                birthday=signup.cleaned_data["parent_birthday"],
                gender=signup.cleaned_data["parent_gender"],
                family=family,
                user=user,
                consent=latest_consent,
                consent_by=user,
                consent_at=timezone.now(),
            )
            person.save()

            # Create child if provided (optional for volunteers)
            if signup.cleaned_data.get("child_name"):
                child = Person.objects.create(
                    membertype=Person.CHILD,
                    name=signup.cleaned_data["child_name"],
                    zipcode=signup.cleaned_data["zipcode"],
                    city=signup.cleaned_data["city"],
                    streetname=signup.cleaned_data["streetname"],
                    housenumber=signup.cleaned_data["housenumber"],
                    floor=signup.cleaned_data["floor"],
                    door=signup.cleaned_data["door"],
                    dawa_id=signup.cleaned_data["dawa_id"],
                    placename=signup.cleaned_data["placename"],
                    email=signup.cleaned_data["child_email"],
                    phone=signup.cleaned_data["child_phone"],
                    birthday=signup.cleaned_data["child_birthday"],
                    gender=signup.cleaned_data["child_gender"],
                    family=family,
                )
                child.save()

            # Update volunteer request to link to the new person
            volunteer_request.person = person
            volunteer_request.finished = timezone.now()
            volunteer_request.save()

            # Process all WAITING items - create Volunteer records and set status to ACTIVE
            for item in waiting_items:
                try:
                    # Create Volunteer record with info from form - use correct logic for department/activity
                    if item.activity:
                        # Activity-specific volunteer
                        volunteer = Volunteer.objects.create(
                            person=person,
                            department=item.activity.department,
                            activity=item.activity,
                            allow_cpdk_contact=signup.cleaned_data.get(
                                "allow_cpdk_contact", False
                            ),
                            start_date=timezone.now().date(),
                            end_date=item.activity.end_date,
                        )
                    else:
                        # Department-level volunteer
                        volunteer = Volunteer.objects.create(
                            person=person,
                            department=item.department,
                            activity=None,
                            allow_cpdk_contact=signup.cleaned_data.get(
                                "allow_cpdk_contact", False
                            ),
                            start_date=timezone.now().date(),
                            end_date=None,
                        )

                    # Try to set the volunteer info fields if they exist
                    try:
                        volunteer.info_reference = signup.cleaned_data.get(
                            "volunteer_info_reference", ""
                        )
                        volunteer.info_whishes = signup.cleaned_data.get(
                            "volunteer_info_whishes", ""
                        )
                        volunteer.save()
                    except Exception as field_error:
                        print(f"Info fields not available yet: {field_error}")

                    # Update status to ACTIVE only if volunteer was created successfully
                    item.status = "ACTIVE"
                    item.finished = timezone.now()
                    item.save()

                    print(
                        f"Created volunteer record {volunteer.id} for {person.name} in {item.department.name}"
                    )

                except Exception as e:
                    print(f"Error creating volunteer record: {e}")
                    messages.error(
                        request, f"Fejl ved oprettelse af frivillig post: {e}"
                    )
                    # Don't update status if there was an error

            # Log in the user
            login(request, user)

            # redirect to success
            messages.success(
                request, "Din konto er oprettet og du er nu registreret som frivillig!"
            )
            return HttpResponseRedirect(reverse("volunteer_account_created"))
        else:
            # Form has errors - make sure form action is correct
            signup.helper.form_action = f"/account/create/volunteer/{token}/"
            return render(
                request,
                "members/volunteer_account_create.html",
                {"signupform": signup, "volunteer_request": volunteer_request},
            )

    # initial load - pre-fill form with volunteer request data
    initial_data = {
        "parent_name": volunteer_request.name,
        "parent_email": volunteer_request.email,
        "parent_phone": volunteer_request.phone,
        "zipcode": volunteer_request.zip,
        "volunteer_info_reference": volunteer_request.info_reference,
        "volunteer_info_whishes": volunteer_request.info_whishes,
    }

    signup = signupForm(initial=initial_data)
    # Override form action to post back to this volunteer account creation URL
    signup.helper.form_action = f"/account/create/volunteer/{token}/"

    return render(
        request,
        "members/volunteer_account_create.html",
        {"signupform": signup, "volunteer_request": volunteer_request},
    )
