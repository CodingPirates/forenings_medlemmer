from members.tests.factories import PersonFactory
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from members.utils.user import (
    is_not_logged_in_and_has_person,
    has_family,
    user_to_family,
    user_to_person,
    has_user,
)

"""
    This checks if user decorators work
"""


class UserDecoratorsTests(TestCase):
    def test_user_decorators(self):
        self.password = (
            "ees9mi6phidaeshei3ahk5ooPah4aixoo7uKeiCh2baazu1remei4oHa0iJegh9k"
        )
        self.client = Client()

        # Create user with Person
        self.person = PersonFactory.create()
        self.person.user.email = "person@example.com"
        self.person.user.username = "person"
        self.person.user.set_password(self.password)
        self.person.save()

        # self.user = UserFactory.Create(username="user", email="user@example.com", password=self.password)
        # Create user without person
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password=self.password
        )

        self.assertEqual(is_not_logged_in_and_has_person(self.person.user), True)
        self.assertEqual(is_not_logged_in_and_has_person(self.user), False)

        self.assertEqual(has_family(self.person.user), True)
        self.assertEqual(has_family(self.user), False)

        self.assertEqual(has_user(self.person.user), True)
        self.assertEqual(has_user(self.user), False)

        self.assertEqual(user_to_family(self.person.user), self.person.family)
        self.assertEqual(user_to_family(self.user), None)

        self.assertEqual(user_to_person(self.person.user), self.person)
        self.assertEqual(user_to_person(self.user), None)
