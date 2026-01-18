from django.test import TestCase
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import User
from members.models.person import Person
from datetime import datetime, timedelta
from django.utils import timezone
from freezegun import freeze_time

from members.tests.factories import (
    PersonFactory,
    ActivityParticipantFactory,
    ActivityFactory,
    PaymentFactory,
)
from members.tests.factories.department_factory import DepartmentFactory
from members.tests.factories.factory_helpers import TIMEZONE
from members.tests.factories.waitinglist_factory import WaitingListFactory
from members.tests.factories.user_factory import UserFactory


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
        PersonFactory(name="Jane Doe", added_at=datetime(2018, 1, 1, tzinfo=TIMEZONE))
        PersonFactory(name="John Doe", added_at=datetime(2017, 1, 1, tzinfo=TIMEZONE))

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

    def create_request_with_permission(self, permission):
        return type(
            "Request",
            (object,),
            {
                "user": type(
                    "User",
                    (object,),
                    {"has_perm": lambda self, perm: perm == permission},
                )()
            },
        )()

    def test_anonymize_person_in_single_member_family_no_permission(self):
        person = PersonFactory()

        request = self.create_request_with_permission("members.non_existing_permission")
        with self.assertRaises(PermissionDenied):
            person.anonymize(request)

    def test_anonymize_person_in_single_member_family_already_anonymized(self):
        person = PersonFactory(
            anonymized=True,
        )

        request = self.create_request_with_permission("members.anoymize_persons")
        with self.assertRaises(PermissionDenied):
            person.anonymize(request)

    def test_anonymize_person_in_single_member_family(self):
        with freeze_time(timezone.now() - timedelta(days=3 * 365)):
            person = PersonFactory()

        birthday = person.birthday
        municipality = person.municipality

        # create waiting list for person
        department = DepartmentFactory()
        WaitingListFactory(person=person, department=department)

        self.assertEqual(person.waitinglist_set.count(), 1)

        request = self.create_request_with_permission("members.anonymize_persons")
        person.anonymize(request)

        self.assertTrue(person.anonymized)
        self.assertEqual(person.name, "Anonymiseret")
        self.assertEqual(person.zipcode, "")
        self.assertEqual(person.municipality, municipality)  # should not be changed

        self.assertIsNotNone(person.birthday)

        # only day changes, not month or year
        self.assertEqual(person.birthday.year, birthday.year)
        self.assertEqual(person.birthday.month, birthday.month)
        self.assertNotEqual(person.birthday.day, birthday.day)

        # verify that person is removed from all waiting lists
        self.assertEqual(person.waitinglist_set.count(), 0)

        # given only one member of family, family should also be anonymized
        self.assertTrue(person.family.anonymized)

    def test_anonymize_single_person_in_multi_member_family(self):
        with freeze_time(timezone.now() - timedelta(days=3 * 365)):
            person_1 = PersonFactory()
            person_2 = PersonFactory(family=person_1.family)

        # create waiting list entries for both person
        department = DepartmentFactory()
        WaitingListFactory(person=person_1, department=department)
        WaitingListFactory(person=person_2, department=department)

        self.assertEqual(department.waitinglist_set.count(), 2)

        # sanity check that they are in the same family
        self.assertEqual(person_1.family, person_2.family)

        request = self.create_request_with_permission("members.anonymize_persons")
        person_1.anonymize(request)

        self.assertTrue(person_1.anonymized)
        self.assertFalse(person_2.anonymized)

        # verify that person_1 is removed from waiting list
        self.assertEqual(department.waitinglist_set.count(), 1)
        self.assertEqual(person_1.waitinglist_set.count(), 0)
        self.assertEqual(person_2.waitinglist_set.count(), 1)

        # given more than one member of family, family should not be anonymized
        self.assertFalse(person_1.family.anonymized)

    def test_anonymize_all_persons_in_multi_member_family(self):
        with freeze_time(timezone.now() - timedelta(days=3 * 365)):
            person_1 = PersonFactory()
            person_2 = PersonFactory(family=person_1.family)

        request = self.create_request_with_permission("members.anonymize_persons")

        # sanity check that are are pointing to same family object
        self.assertEqual(person_1.family, person_2.family)

        person_1.anonymize(request)

        self.assertTrue(person_1.anonymized)
        self.assertFalse(person_1.family.anonymized)  # not yet anonymized

        person_2.anonymize(request)

        self.assertTrue(person_2.anonymized)
        self.assertTrue(person_2.family.anonymized)

    def test_anonymize_person_with_user(self):
        with freeze_time(timezone.now() - timedelta(days=3 * 365)):
            person = PersonFactory()

        user = User.objects.create_user(
            username=person.name, email=person.email, password="password"
        )
        self.assertTrue(user.is_active)

        request = self.create_request_with_permission("members.anonymize_persons")
        person.anonymize(request)

        self.assertTrue(person.anonymized)

        # retrive updated user from database, and verify that user is no longer active
        user = User.objects.get(pk=person.user.pk)

        self.assertEqual(user.first_name, "Anonymiseret")
        self.assertNotEqual(user.email, person.email)  # email should be anonymized
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_active)

    def test_anonymize_person_with_sent_emails(self):
        with freeze_time(timezone.now() - timedelta(days=3 * 365)):
            person = PersonFactory()

        email = person.emailitem_set.create(
            receiver=person.email, subject="Test email", body_text="Test email body"
        )

        request = self.create_request_with_permission("members.anonymize_persons")
        person.anonymize(request)

        self.assertTrue(person.anonymized)

        # retrieve updated email from database, and verify that email is anonymized
        email = person.emailitem_set.get(pk=email.pk)

        self.assertEqual(email.subject, "Anonymiseret")
        self.assertEqual(email.body_text, "")
        self.assertEqual(email.receiver, "")

    ############################################################
    # Tests for is_anonymization_candidate()
    def test_person_created_one_year_ago_is_not_anonymization_candidate(self):
        """Person created 1 year ago cannot be anonymized."""
        # Create person 1 year ago
        one_year_ago = timezone.now() - timedelta(days=1 * 365)
        with freeze_time(one_year_ago):
            person = PersonFactory()

        self.assertFalse(person.is_anonymization_candidate()[0])

    def test_person_created_two_years_ago_without_any_activity_is_anonymization_candidate(
        self,
    ):
        """Person created exactly 2 years ago, without any activity, can be anonymized."""
        # Create person 2 years and 1 day ago
        two_years_ago = timezone.now() - timedelta(days=2 * 365)
        with freeze_time(two_years_ago):
            person = PersonFactory()

        self.assertTrue(person.is_anonymization_candidate()[0])

    def test_person_with_recent_login_is_not_anonymization_candidate(self):
        """Person with recent login should not be a candidate."""
        # Create person 6 years ago
        six_years_ago = timezone.now() - timedelta(days=6 * 365)
        with freeze_time(six_years_ago):
            person = PersonFactory()

        # Create user with recent login (1 year ago)
        user = UserFactory()
        user.last_login = timezone.now() - timedelta(days=1 * 365)
        user.save()
        person.user = user
        person.save()

        self.assertFalse(person.is_anonymization_candidate()[0])

    def test_person_with_non_recent_login_is_anonymization_candidate(self):
        """Person with non-recent login should be a candidate."""
        # Create person 6 years ago
        six_years_ago = timezone.now() - timedelta(days=6 * 365)
        with freeze_time(six_years_ago):
            person = PersonFactory()

        # Create user with non-recent login (2 years and 1 day ago)
        user = UserFactory()
        user.last_login = timezone.now() - timedelta(days=2 * 365 + 1)
        user.save()
        person.user = user
        person.save()

        self.assertTrue(person.is_anonymization_candidate()[0])

    def test_candidate_recent_activity_participation_is_not_anonymization_candidate(
        self,
    ):
        """Person with recent activity participation (2 years ago) should not be a candidate."""
        # Create person 6 years ago
        six_years_ago = timezone.now() - timedelta(days=6 * 365)
        with freeze_time(six_years_ago):
            person = PersonFactory()

        # Create activity that ended 2 years ago
        two_years_ago = timezone.now() - timedelta(days=2 * 365)
        activity = ActivityFactory(
            start_date=(two_years_ago - timedelta(days=30)).date(),
            end_date=two_years_ago.date(),
        )
        ActivityParticipantFactory(person=person, activity=activity)

        self.assertFalse(person.is_anonymization_candidate()[0])

    def test_old_person_no_recent_activity_is_anonymization_candidate(self):
        """Person created long ago with no recent activity or login should be a candidate."""
        # Create person 6 years ago
        six_years_ago = timezone.now() - timedelta(days=6 * 365)
        with freeze_time(six_years_ago):
            person = PersonFactory()

        # Create old activity (7 years ago)
        seven_years_ago = timezone.now() - timedelta(days=7 * 365)
        activity = ActivityFactory(
            start_date=(seven_years_ago - timedelta(days=30)).date(),
            end_date=seven_years_ago.date(),
        )
        ActivityParticipantFactory(person=person, activity=activity)

        # Create user with old login (7 years ago)
        user = UserFactory()
        user.last_login = timezone.now() - timedelta(days=7 * 365)
        user.save()
        person.user = user
        person.save()

        self.assertTrue(person.is_anonymization_candidate()[0])

    def test_user_never_logged_in_is_anonymization_candidate(self):
        """Person with user account that never logged in should be candidate if old enough."""
        # Create person 6 years ago
        six_years_ago = timezone.now() - timedelta(days=6 * 365)
        with freeze_time(six_years_ago):
            person = PersonFactory()

        # Create user with no login date
        user = UserFactory()
        user.last_login = None
        user.save()
        person.user = user
        person.save()

        self.assertTrue(person.is_anonymization_candidate()[0])

    def test_multiple_activities_latest_is_recent_is_not_anonymization_candidate(self):
        """Person with multiple activities, one old and one recent, cannot be anonymized."""
        # Create person 6 years ago
        six_years_ago = timezone.now() - timedelta(days=6 * 365)
        with freeze_time(six_years_ago):
            person = PersonFactory()

        # Create old activity (7 years ago)
        seven_years_ago = timezone.now() - timedelta(days=7 * 365)
        old_activity = ActivityFactory(
            start_date=(seven_years_ago - timedelta(days=30)).date(),
            end_date=seven_years_ago.date(),
        )
        ActivityParticipantFactory(person=person, activity=old_activity)

        # Create recent activity (1 year ago)
        one_year_ago = timezone.now() - timedelta(days=1 * 365)
        recent_activity = ActivityFactory(
            start_date=(one_year_ago - timedelta(days=30)).date(),
            end_date=one_year_ago.date(),
        )
        ActivityParticipantFactory(person=person, activity=recent_activity)

        self.assertFalse(person.is_anonymization_candidate()[0])

    def test_person_created_exactly_two_years_ago_is_anonymization_candidate(self):
        """Test edge case: person created exactly 2 years ago."""
        # Create person exactly 2 years ago
        exactly_two_years_ago = timezone.now() - timedelta(days=2 * 365)
        with freeze_time(exactly_two_years_ago):
            person = PersonFactory()

        self.assertTrue(person.is_anonymization_candidate()[0])

    def test_person_created_over_2_years_with_payments_5_years_is_not_anonymization_candidate(
        self,
    ):
        """Person with payments in the last 5 years cannot be anonymized."""
        # Create person exactly 2 years and 1 day ago
        two_years_and_one_day_ago = timezone.now() - timedelta(days=2 * 365 + 1)
        with freeze_time(two_years_and_one_day_ago):
            person = PersonFactory()

        # Create payment in the last 5 years
        PaymentFactory(person=person, added_at=timezone.now() - timedelta(days=4 * 365))

        self.assertFalse(person.is_anonymization_candidate()[0])

    def test_person_where_other_family_member_has_payments_5_years_is_not_anonymization_candidate(
        self,
    ):
        """Person where other family member has payments in the last 5 years cannot be anonymized."""
        # Create two persons, 6 years ago
        six_years_ago = timezone.now() - timedelta(days=6 * 365)
        with freeze_time(six_years_ago):
            parent = PersonFactory()
            child = PersonFactory(family=parent.family)

        # Create payment for child in the last 5 years
        PaymentFactory(
            person=child,
            family=child.family,
            added_at=timezone.now() - timedelta(days=4 * 365),
        )

        # parent cannot be anonymized, since child has payments in the last 5 years
        self.assertFalse(parent.is_anonymization_candidate()[0])

    def test_person_created_over_2_years_with_payments_over_5_years_is_anonymization_candidate(
        self,
    ):
        """Person with payments more than 5 years ago can be anonymized."""

        # assume today's date: 2025-09-27
        # person created: 2023-09-26 => over 2 years ago
        # payment: 2019-12-31 => over 5 years ago

        with freeze_time(datetime(2023, 9, 26)):
            person = PersonFactory()

        # Create payment last day in fiscal year before 5 years ago
        PaymentFactory(
            person=person, added_at=timezone.make_aware(datetime(2019, 12, 31))
        )

        with freeze_time(datetime(2025, 9, 27)):
            self.assertTrue(person.is_anonymization_candidate()[0])

    def test_person_where_other_family_member_has_payments_over_5_years_is_anonymization_candidate(
        self,
    ):
        """Person where other family member has payments in the last 5 years cannot be anonymized."""
        # Create two persons, 6 years ago

        # assume today's date: 2025-12-31
        # person created: 2019-12-31 => 6 years ago
        # payment: 2019-12-31 => over 5 years ago

        six_years_ago = datetime(2019, 12, 31)
        with freeze_time(six_years_ago):
            parent = PersonFactory()
            child = PersonFactory(family=parent.family)

        # Create payment for child more than 5 years ago
        PaymentFactory(
            person=child,
            family=child.family,
            added_at=timezone.make_aware(datetime(2019, 12, 31)),
        )

        # parent cannot be anonymized, since child has payments in the last 5 years
        with freeze_time(datetime(2025, 12, 31)):
            self.assertTrue(parent.is_anonymization_candidate()[0])

    def test_person_created_recently_is_anonymization_candidate_in_relaxed_mode(self):
        """Person created recently can be anonymized in relaxed mode if no payments."""
        # Create person 1 year ago (recently)
        one_year_ago = timezone.now() - timedelta(days=1 * 365)
        with freeze_time(one_year_ago):
            person = PersonFactory()

        # In normal mode, should fail because created recently
        self.assertFalse(person.is_anonymization_candidate(relaxed=False)[0])

        # In relaxed mode, should pass because creation date check is skipped
        # (assuming no payments and no recent activity)
        self.assertTrue(person.is_anonymization_candidate(relaxed=True)[0])
