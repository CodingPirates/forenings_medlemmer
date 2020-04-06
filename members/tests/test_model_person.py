from django.test import TestCase
from django.core.exceptions import ValidationError
from members.models.person import Person
from datetime import datetime
from freezegun import freeze_time

from members.tests.factories import PersonFactory
from members.tests.factories.factory_helpers import TIMEZONE


class TestModelPerson(TestCase):
    def mock_reference_time(self, time):
        def mock(timezone):
            pass

        return mock

    def test_age_years(self):
        with freeze_time(datetime(2010, 3, 2)):
            person = PersonFactory(birthday=datetime(2000, 1, 1))
            self.assertEqual(person.age_years(), 10)

    def test_can_create_person(self):
        PersonFactory()  # no error should be thrown

    def test_saving_and_retrieving_persons(self):
        PersonFactory(name="Jane Doe", added=datetime(2018, 1, 1, tzinfo=TIMEZONE))
        PersonFactory(name="John Doe", added=datetime(2017, 1, 1, tzinfo=TIMEZONE))

        saved_persons = Person.objects.all()
        self.assertEqual(saved_persons.count(), 2)

        # retrieved in order of 'added' field
        self.assertEqual(saved_persons[0].name, "John Doe")
        self.assertEqual(saved_persons[1].name, "Jane Doe")

    def test_build_many(self):
        persons = PersonFactory.build_batch(size=20)
        self.assertEqual(len(persons), 20)
        self.assertEqual(Person.objects.count(), 0)
        self.assertFalse(Person.objects.exists())

    def test_creating_many(self):
        PersonFactory.create_batch(size=20)
        self.assertEqual(Person.objects.count(), 20)

    def test_firstname_allows_dash_in_names(self):
        person = PersonFactory(name="Hans-Christian Jensen Eriksen")
        self.assertEqual(person.firstname(), "Hans-Christian")

    def test_firstname_no_lastname(self):
        person = PersonFactory(name="Margrethe")
        self.assertEqual(person.firstname(), "Margrethe")

    def test_cannot_create_person_with_no_name(self):
        with self.assertRaises(ValidationError):
            person = PersonFactory(name="")
            person.full_clean()

    def test_cannot_change_person_to_unnamed(self):
        person = PersonFactory()
        with self.assertRaises(ValidationError):
            person.name = ""
            person.full_clean()

    def test_string_representation(self):
        person = PersonFactory()
        self.assertEqual(person.name, str(person))

    def test_defaults_to_parent(self):
        person = PersonFactory()
        self.assertEqual(person.membertype, Person.PARENT)

    def test_defaults_to_not_deleted(self):
        person = PersonFactory()
        self.assertEqual(person.deleted_dtm, None)

    def test_defaults_to_no_certificate(self):
        person = PersonFactory()
        self.assertEqual(person.has_certificate, None)
