#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
from datetime import date as _date, datetime as _datetime, time as _time
from django.utils import timezone
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from members.models.volunteerrequestitem import VolunteerRequestItem
from members.models import VolunteerRequest, Department, Activity, Person


def _get_future_activities():
    now = timezone.now()
    qs = Activity.objects.filter(activitytype__id__in=["FORLØB", "ARRANGEMENT"])
    future = []
    for a in qs:
        end = None
        for fld in ("end_date", "end", "finish"):
            if hasattr(a, fld):
                end = getattr(a, fld)
                break
        # if no end date, include
        if end is None:
            future.append(a)
            continue

        # normalize date -> datetime (treat a date as end of that day)
        end_dt = end
        if isinstance(end, _date) and not isinstance(end, _datetime):
            end_dt = _datetime.combine(end, _time.max)

        # ensure both sides are comparable w.r.t timezone-awareness
        if timezone.is_aware(now) and timezone.is_naive(end_dt):
            end_dt = timezone.make_aware(end_dt, timezone.get_current_timezone())
        elif timezone.is_naive(now) and timezone.is_aware(end_dt):
            end_dt = timezone.make_naive(end_dt, timezone.get_current_timezone())

        if end_dt and end_dt > now:
            future.append(a)
    return future


def _create_volunteer_request_and_items(form_data, selected_person_pk=None):
    vr = VolunteerRequest()
    field_names = {f.name for f in VolunteerRequest._meta.get_fields()}

    if selected_person_pk and "person" in field_names:
        try:
            vr.person = Person.objects.get(pk=selected_person_pk)
        except Person.DoesNotExist:
            vr.person = None

    mapping = {
        "info_name": "name",
        "info_email": "email",
        "info_phone": "phone",
        "info_age": "age",
        "info_zip": "zip",
        "info_reference": "reference",
        "info_whishes": "whishes",
    }
    for model_field, form_key in mapping.items():
        if model_field in field_names and form_key in form_data:
            setattr(vr, model_field, form_data.get(form_key))

    vr.save()

    created_items = []
    depts = form_data.get("departments", [])
    acts = form_data.get("activities", [])

    for dept_pk in depts:
        try:
            dept = Department.objects.get(pk=dept_pk)
        except Department.DoesNotExist:
            continue
        vri = VolunteerRequestItem(volunteer_request=vr, department=dept)
        vri.save()
        created_items.append(vri)

    for act_pk in acts:
        try:
            act = Activity.objects.get(pk=act_pk)
        except Activity.DoesNotExist:
            continue
        vri = VolunteerRequestItem(
            volunteer_request=vr, department=act.department, activity=act
        )
        vri.save()
        created_items.append(vri)

    return vr, created_items


def volunteer_entry(request):
    try:
        departments = Department.objects.filter(closed_dtm=None).order_by("name")
    except Exception:
        print
        departments = Department.objects.all()

    activities = _get_future_activities()

    persons = []
    if request.user.is_authenticated:
        try:
            persons = Person.objects.filter(account=request.user)
        except Exception:
            try:
                persons = request.user.person_set.all()
            except Exception:
                persons = Person.objects.none()

    if request.method == "POST":
        data = {
            "name": request.POST.get("name", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "age": request.POST.get("age", "").strip(),
            "zip": request.POST.get("zip", "").strip(),
            "reference": request.POST.get("reference", "").strip(),
            "whishes": request.POST.get("whishes", "").strip(),
            "departments": request.POST.getlist("departments"),
            "activities": request.POST.getlist("activities"),
        }

        if not data["departments"] and not data["activities"]:
            messages.error(request, "Du skal vælge mindst en afdeling eller aktivitet.")
            return render(
                request,
                "members/volunteer.html",
                {
                    "departments": departments,
                    "activities": activities,
                    "persons": persons,
                },
            )

        if request.user.is_authenticated and request.POST.get("person"):
            selected_person_pk = request.POST.get("person")
            vr, items = _create_volunteer_request_and_items(
                data, selected_person_pk=selected_person_pk
            )
            messages.success(request, "Tak — din anmodning er modtaget.")
            return redirect("volunteer_signup")

        if not request.user.is_authenticated:
            email = data.get("email")
            if not email:
                messages.error(
                    request, "Email er påkrævet for at kunne validere din anmodning."
                )
                return render(
                    request,
                    "members/volunteer.html",
                    {
                        "departments": departments,
                        "activities": activities,
                        "persons": persons,
                        "form": data,
                    },
                )

            fixed = os.environ.get("FIXED_RANDOM")
            if fixed:
                try:
                    token = str(int(fixed))[-6:].zfill(6)
                except Exception:
                    token = fixed[:6]
            else:
                token = str(random.randint(100000, 999999))

            request.session["volunteer_signup_pending"] = {
                "token": token,
                "form": data,
                "created": timezone.now().isoformat(),
            }
            request.session.modified = True

            subject = "Bekræft din email for frivillig-anmodning"
            message = f"Din bekræftelseskode er: {token}"
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            try:
                send_mail(subject, message, from_email, [email], fail_silently=False)
            except Exception:
                messages.warning(
                    request,
                    "Kunne ikke sende email — kontroller mailkonfiguration. Token: "
                    + token,
                )

            return redirect("volunteer_verify")

    return render(
        request,
        "members/volunteer.html",
        {"departments": departments, "activities": activities, "persons": persons},
    )


def volunteer_verify(request):
    pending = request.session.get("volunteer_signup_pending")
    if not pending:
        messages.error(request, "Ingen ventende anmodning fundet. Start forfra.")
        return redirect("volunteer_signup")

    if request.method == "POST":
        code = request.POST.get("token", "").strip()
        if code == str(pending.get("token")):
            form_data = pending.get("form", {})
            vr, items = _create_volunteer_request_and_items(
                form_data, selected_person_pk=None
            )
            try:
                del request.session["volunteer_signup_pending"]
            except KeyError:
                pass
            messages.success(
                request, "Din email er bekræftet og anmodningen er oprettet."
            )
            return redirect("volunteer_signup")
        else:
            messages.error(request, "Ugyldig kode. Prøv igen.")

    return render(
        request,
        "members/volunteer_verify.html",
        {"email": pending.get("form", {}).get("email")},
    )
