# FILE: members/tests/test_middleware/test_consent_middleware.py
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from members.models import Consent, Person, Family
from members.middleware.consent_middleware import ConsentMiddleware


class TestConsentMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(username="testuser", password="password")

        # Create a Family object if family_id is a foreign key
        self.family = Family.objects.create(email="Test@Family.none")

        # Pass the family object when creating the Person
        self.person = Person.objects.create(user=self.user, family=self.family)
        self.middleware = ConsentMiddleware(lambda request: None)

    def test_user_without_consent_redirected(self):
        # Create a new consent
        Consent.objects.create(released_at=timezone.now())

        # Simulate a request from an authenticated user without consent
        request = self.factory.get("/some-protected-page/")
        request.user = self.user
        request.session = {}

        response = self.middleware(request)

        # Assert that the user is redirected to the consent page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("consent_page"))
        self.assertEqual(request.session.get("original_url"), "/some-protected-page/")

    def test_user_accepting_consent(self):
        # Create a new consent
        consent = Consent.objects.create(released_at=timezone.now())

        # Simulate the user accepting the consent
        self.person.consent = consent
        self.person.save()

        # Simulate a request from an authenticated user who has accepted consent
        request = self.factory.get("/some-protected-page/")
        request.user = self.user
        request.session = {}

        response = self.middleware(request)
        # Assert that the user is not redirected and can access the page
        self.assertIsNone(response)

    def test_user_redirected_for_new_updated_consent(self):
        # Create an initial consent and assign it to the user
        old_consent = Consent.objects.create(
            released_at=timezone.now() - timezone.timedelta(days=10)
        )
        self.person.consent = old_consent
        self.person.save()

        # Create a new updated consent
        new_consent = Consent.objects.create(released_at=timezone.now())

        # Explicitly reference new_consent to avoid flake8 warnings
        self.assertIsNotNone(new_consent)

        # Simulate a request from an authenticated user with outdated consent
        request = self.factory.get("/some-protected-page/")
        request.user = self.user
        request.session = {}

        response = self.middleware(request)

        # Assert that the user is redirected to the consent page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("consent_page"))
        self.assertEqual(request.session.get("original_url"), "/some-protected-page/")
