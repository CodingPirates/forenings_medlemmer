from datetime import datetime
from dateutil.relativedelta import relativedelta

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
from .factories import ActivityFactory


# set MESSAGE_STORAGE to CookieStorage to support django messaging framework
@override_settings(
    MESSAGE_STORAGE="django.contrib.messages.storage.cookie.CookieStorage"
)
class TestAdminActions(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = AdminActions(Activity, admin.site)

        self.union = UnionFactory()
        self.department = DepartmentFactory(union=self.union, closed_dtm=None)

        self.user = User.objects.create_user(
            username="user",
            password="password",
            is_superuser=True,
        )

        # activity starts in two days, so we can test situation where person is too young today, but will be ok at activity start
        self.activity_starting_in_two_days = ActivityFactory(
            start_date=datetime.now() + relativedelta(days=2),
            end_date=datetime.now() + relativedelta(months=1),
            min_age=7,
            max_age=17,
            department=self.department,
            union=self.union,
        )
        self.activity_starting_in_two_days.save()

        # activity started two days ago, so we can test situation where person wasn't old enough at activity start, but is today
        self.activity_started_two_days_ago = ActivityFactory(
            start_date=datetime.now() - relativedelta(days=2),
            end_date=datetime.now() + relativedelta(months=1),
            min_age=7,
            max_age=17,
            department=self.department,
            union=self.union,
        )
        self.activity_started_two_days_ago.save()

        self.family = Family()
        self.family.save()

        # create test persons with specific ages (will have birthday a week ago)
        self.person_min_age = self.create_person_and_waiting_list_entry(
            name="person_min_age", age=7
        )
        self.person_within_age_range = self.create_person_and_waiting_list_entry(
            name="person_within_age_range", age=10
        )
        self.person_max_age = self.create_person_and_waiting_list_entry(
            name="person_max_age", age=17
        )
        self.person_above_max_age = self.create_person_and_waiting_list_entry(
            name="person_above_max_age", age=18
        )
        self.person_without_age = self.create_person_and_waiting_list_entry(
            name="person_without_age"
        )

        # activity starts in two days, person has birthday two weeks after
        self.person_too_young = self.create_person_and_waiting_list_entry(
            name="person_too_young",
            birthday=(datetime.now() - relativedelta(years=7) + relativedelta(weeks=2)),
        )

        # activity starts in two days, person has birthday tomorrow
        self.person_becomes_min_age_tomorrow = (
            self.create_person_and_waiting_list_entry(
                name="person_becomes_min_age_tomorrow",
                birthday=(
                    datetime.now() - relativedelta(years=7) + relativedelta(days=1)
                ),
            )
        )

        # activity started two days ago, person had birthday yesterday
        self.person_became_min_age_yesterday = (
            self.create_person_and_waiting_list_entry(
                name="person_became_min_age_yesterday",
                birthday=(
                    datetime.now() - relativedelta(years=7) - relativedelta(days=1)
                ),
            )
        )

        # setup email template
        EmailTemplate.objects.create(
            idname="ACT_INVITE",
            subject="test email subject",
        )

    def create_person_and_waiting_list_entry(self, name=None, age=None, birthday=None):
        person_birthday = None
        if age is not None:
            person_birthday = (
                datetime.now() - relativedelta(years=age) - relativedelta(weeks=1)
            )
            person_name = f"Testperson {age} år, født {person_birthday}"
        elif birthday is not None:
            person_birthday = birthday
            person_name = f"Testperson født {person_birthday}"
        else:
            person_name = "Testperson uden fødselsdato"

        if name is not None:
            person_name = name

        if person_birthday is not None:
            person = Person.objects.create(
                name=person_name,
                family=self.family,
                birthday=person_birthday,
            )
        else:
            person = Person.objects.create(name=person_name, family=self.family)

        WaitingList(
            person=person,
            department=self.department,
            on_waiting_list_since=datetime.now() - relativedelta(days=1),
        ).save()

        return person

    def create_mock_request_object(self, activity):
        request = self.factory.post("/admin/members/activity/")
        request._messages = messages.storage.default_storage(
            request
        )  # Add support for django messaging framework
        request.method = "POST"
        request.POST = {
            "activity": activity.id,
            "department": activity.department.id,
            "expire": datetime.now() + relativedelta(months=1),
            "email_text": "Lidt ekstra tekst",
        }
        request.user = self.user

        return request

    # test for person who is within age range for activity in future
    def test_invite_many_to_activity_starting_in_two_days(self):
        request = self.create_mock_request_object(
            activity=self.activity_starting_in_two_days
        )

        # Call the method. Returns None if successful, so no need to store response
        self.admin.invite_many_to_activity_action(request, Person.objects.all())

        # Assert that the correct persons are invited
        invitations = ActivityInvite.objects.all()

        self.assertEqual(
            invitations.count(),
            5,
            "Actually invited: '"
            + ", ".join(str(invitation.person.name) for invitation in invitations)
            + "'",
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_within_age_range,
                activity=self.activity_starting_in_two_days,
            ).exists()
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_min_age, activity=self.activity_starting_in_two_days
            ).exists()
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_max_age, activity=self.activity_starting_in_two_days
            ).exists()
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_becomes_min_age_tomorrow,
                activity=self.activity_starting_in_two_days,
            ).exists()
        )

        self.assertTrue(
            invitations.filter(
                person=self.person_became_min_age_yesterday,
                activity=self.activity_starting_in_two_days,
            ).exists()
        )

    # test for person who is within age range for activity in past
    def test_invite_many_to_activity_started_two_days_ago(self):
        request = self.create_mock_request_object(
            activity=self.activity_started_two_days_ago
        )

        # Call the method. Returns None if successful, so no need to store response
        self.admin.invite_many_to_activity_action(request, Person.objects.all())

        # Assert that the correct persons are invited
        invitations = ActivityInvite.objects.all()

        self.assertEqual(
            invitations.count(),
            4,
            "Actually invited: '"
            + ", ".join(str(invitation.person.name) for invitation in invitations)
            + "'",
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_within_age_range,
                activity=self.activity_started_two_days_ago,
            ).exists()
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_min_age, activity=self.activity_started_two_days_ago
            ).exists()
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_max_age, activity=self.activity_started_two_days_ago
            ).exists()
        )
        self.assertTrue(
            invitations.filter(
                person=self.person_became_min_age_yesterday,
                activity=self.activity_started_two_days_ago,
            ).exists()
        )
