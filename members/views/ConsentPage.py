from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from members.models import Consent, Person


# @login_required
def consent_page(request):
    latest_consent = (
        Consent.objects.filter(
            released_at__isnull=False, released_at__lte=timezone.now()
        )
        .order_by("-released_at")
        .first()
    )

    has_consented = False
    consent_at = ""
    viewonly = True
    if request.user.is_authenticated:
        person = Person.objects.get(user=request.user)
        if person.consent is not None:
            has_consented = person.consent == latest_consent
        consent_at = person.consent_at
        viewonly = False

        if request.method == "POST" and not has_consented:
            person.consent = latest_consent
            person.consent_at = timezone.now()
            person.consent_by_id = request.user.id
            person.save()
            # Redirect to the original URL if it exists
            original_url = request.session.pop("original_url", None)
            if original_url:
                return redirect(original_url)
            else:
                return redirect(reverse("entry_page"))

    return render(
        request,
        "members/consent_page.html",
        {
            "consent": latest_consent,
            "consent_id": latest_consent.id,
            "consent_released_at": latest_consent.released_at,
            "consent_title": latest_consent.title,
            "consent_text": latest_consent.text,
            "has_consented": has_consented,
            "consent_at": consent_at,
            "viewonly": viewonly,
        },
    )
