from members.tests.factories import PersonFactory
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client

"""
    This checks if users get redirected to /admin-signup/ when they dont have a family
"""


class LoadWhenNoFamilyTest(TestCase):
    def test_load_when_no_family(self):
        self.password = (
            "ees9mi6phidaeshei3ahk5ooPah4aixoo7uKeiCh2baazu1remei4oHa0iJegh9k"
        )
        self.client = Client()

        # Create user with Person
        self.person = PersonFactory.create()
        self.person.user.email = "person@example.com"
        self.person.user.username = "person"
        self.person.user.set_password(self.password)
        self.person.user.save()
        self.person.save()

        # self.user = UserFactory.Create(username="user", email="user@example.com", password=self.password)
        # Create user without person
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password=self.password
        )

        # Log into user without person
        logged_in = self.client.login(username="user", password=self.password)
        self.assertTrue(logged_in)

        # Middleware should force profile/family creation globally
        self.assertRedirects(
            self.client.get("/"),
            "/admin_signup/",
        )

        session = self.client.session
        session.pop("original_url", None)
        session.save()

        # Check for redirect
        response = self.client.get("/department_signup")
        self.assertRedirects(
            response,
            "/admin_signup/",
        )
        self.assertEqual(self.client.session.get("original_url"), "/department_signup")

        # Log into user with person
        self.client.logout()
        logged_in = self.client.login(username="person", password=self.password)
        self.assertTrue(logged_in)

        # Check for no redirect
        self.assertEqual(self.client.get("/department_signup").status_code, 200)
