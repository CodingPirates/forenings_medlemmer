from django.test import TestCase
from django.core.exceptions import ValidationError
from members.models import Membership
from .factories import UnionFactory, PersonFactory
from datetime import date


class TestModelMembership(TestCase):
    def test_create_membership_same_year(self):
        # Creates two memberships in the same year.
        person = PersonFactory.create()
        union = UnionFactory.create()
        Membership.objects.create(
            person=person, union=union, sign_up_date=date(2020, 3, 14)
        )
        with self.assertRaises(ValidationError):
            Membership.objects.create(
                person=person, union=union, sign_up_date=date(2020, 5, 14)
            )
