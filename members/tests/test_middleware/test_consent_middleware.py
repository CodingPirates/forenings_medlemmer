# FILE: members/tests/test_middleware/test_consent_middleware.py
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from members.models import Consent, Person, Family, Volunteer
from members.middleware.consent_middleware import ConsentMiddleware
from members.tests.factories import DepartmentFactory


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

    def test_user_without_person_redirected_to_admin_signup(self):
        user_without_person = User.objects.create_user(
            username="noperson", password="password"
        )

        request = self.factory.get("/some-protected-page/")
        request.user = user_without_person
        request.session = {}

        response = self.middleware(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("admin_signup"))
        self.assertEqual(request.session.get("original_url"), "/some-protected-page/")

    def test_existing_original_url_not_overwritten_by_consent_redirect(self):
        Consent.objects.create(released_at=timezone.now())

        request = self.factory.get("/family/")
        request.user = self.user
        request.session = {"original_url": "/activities/?page=2"}

        response = self.middleware(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("consent_page"))
        self.assertEqual(request.session.get("original_url"), "/activities/?page=2")

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


class TestConsentMiddlewareIntegration(TestCase):
    def setUp(self):
        self.password = "supersecurepassword"
        self.client = Client()
        self.user = User.objects.create_user(
            username="login-only-user",
            email="login-only@example.com",
            password=self.password,
        )
        self.department = DepartmentFactory.create(closed_dtm=None)

    def test_logged_in_user_without_person_is_forced_to_signup_before_consent(self):
        logged_in = self.client.login(
            username="login-only-user", password=self.password
        )
        self.assertTrue(logged_in)

        response = self.client.get("/", follow=False)

        self.assertRedirects(response, "/admin_signup/")
        self.assertEqual(self.client.session.get("original_url"), "/")

    def test_consent_page_redirects_to_admin_signup_when_person_is_missing(self):
        logged_in = self.client.login(
            username="login-only-user", password=self.password
        )
        self.assertTrue(logged_in)

        response = self.client.get(reverse("consent_page"), follow=False)

        self.assertRedirects(response, reverse("admin_signup"))

    def test_admin_signup_creates_person_and_volunteer_for_logged_in_user(self):
        logged_in = self.client.login(
            username="login-only-user", password=self.password
        )
        self.assertTrue(logged_in)

        response = self.client.post(
            reverse("admin_signup"),
            {
                "form_id": "admin_fam",
                "volunteer_gender": Person.MALE,
                "volunteer_name": "Kaptajn Testperson",
                "volunteer_birthday": "1980-03-05",
                "volunteer_email": "captain@example.com",
                "volunteer_phone": "12345678",
                "volunteer_department": str(self.department.pk),
                "search_address": "",
                "streetname": "Testvej",
                "housenumber": "10",
                "floor": "",
                "door": "",
                "placename": "",
                "zipcode": "5000",
                "city": "Odense C",
                "dawa_id": "",
                "manual_entry": "False",
            },
            follow=False,
        )

        self.assertRedirects(response, reverse("family_detail"))

        person = Person.objects.get(user=self.user)
        self.assertEqual(person.family.email, "captain@example.com")
        self.assertTrue(
            Volunteer.objects.filter(person=person, department=self.department).exists()
        )

    def test_admin_signup_redirects_to_family_when_user_already_has_person(self):
        family = Family.objects.create(email="existing@example.com")
        Person.objects.create(
            user=self.user,
            family=family,
            membertype=Person.PARENT,
            name="Eksisterende Bruger",
        )

        logged_in = self.client.login(
            username="login-only-user", password=self.password
        )
        self.assertTrue(logged_in)

        response = self.client.get(reverse("admin_signup"), follow=False)

        self.assertRedirects(response, reverse("family_detail"))

    def test_admin_signup_retry_after_existing_person_redirects_instead_of_showing_family_exists_error(
        self,
    ):
        family = Family.objects.create(email="captain@example.com")
        Person.objects.create(
            user=self.user,
            family=family,
            membertype=Person.PARENT,
            name="Kaptajn Testperson",
            email="captain@example.com",
        )

        logged_in = self.client.login(
            username="login-only-user", password=self.password
        )
        self.assertTrue(logged_in)

        response = self.client.post(
            reverse("admin_signup"),
            {
                "form_id": "admin_fam",
                "volunteer_gender": Person.MALE,
                "volunteer_name": "Kaptajn Testperson",
                "volunteer_birthday": "1980-03-05",
                "volunteer_email": "captain@example.com",
                "volunteer_phone": "12345678",
                "volunteer_department": str(self.department.pk),
                "search_address": "",
                "streetname": "Testvej",
                "housenumber": "10",
                "floor": "",
                "door": "",
                "placename": "",
                "zipcode": "5000",
                "city": "Odense C",
                "dawa_id": "",
                "manual_entry": "False",
            },
            follow=False,
        )

        self.assertRedirects(response, reverse("family_detail"))

    def test_admin_signup_with_empty_department_shows_form_error_instead_of_crashing(
        self,
    ):
        logged_in = self.client.login(
            username="login-only-user", password=self.password
        )
        self.assertTrue(logged_in)

        response = self.client.post(
            reverse("admin_signup"),
            {
                "form_id": "admin_fam",
                "volunteer_gender": Person.MALE,
                "volunteer_name": "Kaptajn Testperson",
                "volunteer_birthday": "1980-03-05",
                "volunteer_email": "captain@example.com",
                "volunteer_phone": "12345678",
                "volunteer_department": "",
                "search_address": "",
                "streetname": "Testvej",
                "housenumber": "10",
                "floor": "",
                "door": "",
                "placename": "",
                "zipcode": "5000",
                "city": "Odense C",
                "dawa_id": "",
                "manual_entry": "False",
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dette felt er påkrævet")

    def test_person_save_normalizes_empty_municipality_id(self):
        family = Family.objects.create(email="normalize@example.com")
        person = Person(
            family=family,
            membertype=Person.PARENT,
            name="Normalize Kommune",
        )
        person.municipality_id = ""

        person.save()

        person.refresh_from_db()
        self.assertIsNone(person.municipality)
