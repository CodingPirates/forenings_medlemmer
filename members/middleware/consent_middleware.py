from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from members.models import Consent, Person


class ConsentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bypass consent check for the consent page itself and other exceptions
        exempt_paths = [reverse("consent_page"), "/account/logout/"]
        if request.path in exempt_paths:
            return self.get_response(request)

        if request.user.is_authenticated:
            person = Person.objects.filter(user=request.user).first()
            if person:
                latest_consent = (
                    Consent.objects.filter(
                        released_at__isnull=False, released_at__lte=timezone.now()
                    )
                    .order_by("-released_at")
                    .first()
                )

                if latest_consent:
                    if (
                        not person.consent
                        or person.consent.released_at < latest_consent.released_at
                    ):
                        # Store the original URL in the session
                        request.session["original_url"] = request.path
                        return redirect(reverse("consent_page"))

        response = self.get_response(request)
        return response
