from django.shortcuts import get_object_or_404, render
from members.models import Consent


def consent_preview(request, consent_id):
    consent = get_object_or_404(Consent, id=consent_id)
    return render(request, "members/consent_popup.html", {"consent": consent})
