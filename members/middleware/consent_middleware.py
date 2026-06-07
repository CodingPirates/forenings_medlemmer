from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from members.models import Consent, Person


class ConsentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _remember_original_url(request):
        request.session.setdefault("original_url", request.get_full_path())

    def __call__(self, request):
        # Ignore static/media/favicon requests for original_url
        if (
            request.path.startswith("/static/")
            or request.path.startswith("/media/")
            or request.path == "/favicon.ico"
        ):
            return self.get_response(request)

        if request.user.is_authenticated:
            admin_signup_path = reverse("admin_signup")
            consent_page_path = reverse("consent_page")
            exempt_paths = [admin_signup_path, consent_page_path, "/account/logout/"]

            person = Person.objects.filter(user=request.user).first()
            if not person:
                if request.path not in exempt_paths:
                    self._remember_original_url(request)
                    return redirect(admin_signup_path)
                return self.get_response(request)

            if request.path in exempt_paths:
                return self.get_response(request)

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
                        # Store the original URL in the session unless one already exists
                        self._remember_original_url(request)
                        return redirect(reverse("consent_page"))

        response = self.get_response(request)
        return response
