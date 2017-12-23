from django.test import TestCase
from members.models.family import Family
from members.models.person import Person
from datetime import datetime
from freezegun import freeze_time


class TestModelPerson(TestCase):
    def setUp(self):
        self.family = Family()
        self.family.save()

        self.person = Person(
            family=self.family
        )
        self.person.save()

    def mock_reference_time(self, time):
        def mock(timezone):
            pass

        return mock

    def test_age_years(self):
        with freeze_time(datetime(2010, 3, 2, 12, 0, 0)):
            self.person.birthday = datetime(2000, 1, 1, 12, 0, 0)
            self.person.save()
            self.assertEqual(self.person.age_years(), 10)

    def test_firstname(self):
        self.person.name = "Foo-Foo Bar Baz"
        self.person.save()
        self.assertEqual(self.person.firstname(), "Foo-Foo")
