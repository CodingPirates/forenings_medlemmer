# members/views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from members.models import Consent


def consent_popup(request):
    consent_id = request.GET.get("consent_id")
    if consent_id:
        consent = get_object_or_404(Consent, id=consent_id)
    else:
        consent = (
            Consent.objects.filter(
                released_at__isnull=False, released_at__lte=timezone.now()
            )
            .order_by("-released_at")
            .first()
        )
    return render(request, "members/consent_popup.html", {"consent": consent})
