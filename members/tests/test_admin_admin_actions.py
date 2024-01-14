from datetime import datetime, timedelta

from django.test import TestCase, RequestFactory, override_settings
from django.contrib import admin, messages
from django.contrib.auth.models import User

from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.emailtemplate import EmailTemplate
from members.models.person import Person
from members.models.family import Family
from members.models.waitinglist import WaitingList
from members.admin.admin_actions import AdminActions

from .factories import UnionFactory
from .factories import DepartmentFactory


# set MESSAGE_STORAGE to CookieStorage to support django messaging framework
@override_settings(
    MESSAGE_STORAGE="django.contrib.messages.storage.cookie.CookieStorage"
)
class TestAdminActions(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = AdminActions(Activity, admin.site)

        self.union = UnionFactory()
        self.department = DepartmentFactory(union=self.union)

        self.user = User.objects.create_user(
            username="user",
            password="password",
            is_superuser=True,
        )

        # logic for inviting is based on activity date, not current date, so we use fixed dates
        self.activity = Activity(
            start_date=datetime.fromisoformat(str(datetime.now().year) + "-01-01"),
            end_date=datetime.fromisoformat(str(datetime.now().year) + "-12-31"),
            min_age=7,
            max_age=17,
            department=self.department,
            union=self.union,
        )
        self.activity.save()

        self.family = Family()
        self.family.save()

        # create test persons with specific ages
        self.person_too_young = self.create_person_and_waiting_list_entry(age=5)
        self.person_exactly_start_age = self.create_person_and_waiting_list_entry(age=7)
        self.person_correct_age = self.create_person_and_waiting_list_entry(age=10)
        self.person_exactly_end_age = self.create_person_and_waiting_list_entry(age=17)
        self.person_too_old = self.create_person_and_waiting_list_entry(age=18)

        self.person_too_young_at_activity_start = (
            self.create_person_and_waiting_list_entry(
                birthday=str(datetime.now().year - 7) + "-01-02"
            )
        )

        # setup email template
        EmailTemplate.objects.create(
            idname="ACT_INVITE",
            subject="test email subject",
        )

    def create_person_and_waiting_list_entry(self, age=None, birthday=None):
        if age is not None:
            person_birthday = str(datetime.now().year - age) + "-01-01"
            person_name = f"Testperson {age} år, født {person_birthday}"
        elif birthday is not None:
            person_birthday = birthday
            person_name = f"Testperson født {person_birthday} år"
        else:
            raise ValueError("Either age or birthday must be specified")

        person = Person.objects.create(
            name=person_name,
            family=self.family,
            birthday=datetime.fromisoformat(person_birthday),
        )
        WaitingList(
            person=person,
            department=self.department,
            on_waiting_list_since=datetime.now() - timedelta(days=1),
        ).save()

        return person

    def create_mock_request_object(self):
        request = self.factory.post("/admin/members/activity/")
        request._messages = messages.storage.default_storage(
            request
        )  # Add support for django messaging framework
        request.method = "POST"
        request.POST = {
            "activity": "1",
            "department": "1",
            "expire": datetime.fromisoformat(f"{datetime.now().year}-12-31"),
            "email_text": "Lidt ekstra tekst",
        }
        request.user = self.user

        return request

    # test for person who is within age range
    def test_invite_many_to_activity_action_correct_persons_are_invited(self):
        request = self.create_mock_request_object()

        # Call the method. Returns None if successful, so no need to store response
        self.admin.invite_many_to_activity_action(request, Person.objects.all())

        # Assert that the correct persons are invited
        invitations = ActivityInvite.objects.all()

        self.assertEqual(invitations.count(), 4)
        self.assertTrue(
            invitations.filter(
                person=self.person_correct_age, activity=self.activity
            ).exists()
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_exactly_start_age, activity=self.activity
            ).exists()
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_exactly_end_age, activity=self.activity
            ).exists()
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_too_young_at_activity_start, activity=self.activity
            ).exists()
        )
