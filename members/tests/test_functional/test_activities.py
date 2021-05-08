import datetime
import socket
import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from factory import Faker
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait

from members.tests.factories import ActivityFactory, VolunteerFactory, PersonFactory

from members.tests.factories.person_factory import UserFactory

"""
This test goes to the activities list.
"""


class ActivitiesTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.activity_arrangement = ActivityFactory.create(
            open_invite=True,
            signup_closing=Faker("future_datetime", end_date="+100d"),
            min_age=5,
            max_age=90,
            name="Arrangement",
            activitytype_id="ARRANGEMENT",
        )
        self.activity_arrangement.save()
        self.activity_forløb = ActivityFactory.create(
            open_invite=True,
            signup_closing=Faker("future_datetime", end_date="+100d"),
            min_age=5,
            max_age=90,
            name="Forløb",
            activitytype_id="FORLØB",
        )
        self.activity_forløb.save()
        self.activity_foreningsmedlemskab = ActivityFactory.create(
            open_invite=True,
            signup_closing=Faker("future_datetime", end_date="+100d"),
            min_age=5,
            max_age=90,
            name="Foreningsmedlemskab",
            activitytype_id="FORENINGSMEDLEMSKAB",
        )
        self.activity_foreningsmedlemskab.save()
        self.activity_støttemedlemskab = ActivityFactory.create(
            open_invite=True,
            signup_closing=Faker("future_datetime", end_date="+100d"),
            min_age=5,
            max_age=90,
            name="Støttemedlemskab",
            activitytype_id="STØTTEMEDLEMSKAB",
        )
        self.activity_støttemedlemskab.save()
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/activities_list_final.png")
        self.browser.quit()

    def test_activities(self):
        email = "some_email@bob.gl"
        password = "MySecret"
        volunteer = VolunteerFactory.create(
            person=PersonFactory.create(
                birthday=Faker("date_between", start_date="-50y", end_date="-10y"),
                user=UserFactory.create(username=email, email=email, password=password),
            )
        )
        volunteer.person.user.set_password(password)
        volunteer.person.user.save()
        volunteer.person.birthday = datetime.date(1980, 1, 10)

        # Login
        self.browser.get(f"{self.live_server_url}/account/login")
        self.browser.save_screenshot("test-screens/login.png")
        field = self.browser.find_element_by_name("username")
        field.send_keys(email)
        field = self.browser.find_element_by_name("password")
        field.send_keys(password)

        self.browser.save_screenshot("test-screens/activities_login_filled.png")

        self.browser.find_element_by_xpath("//input[@value='Log ind']").click()
        self.browser.save_screenshot("test-screens/activities_logged_in.png")
        self.assertIn(
            "Jeres familie",
            [
                e.text
                for e in self.browser.find_elements_by_xpath(
                    "//body/descendant-or-self::*"
                )
            ],
        )

        # Loads the activities
        self.browser.find_element_by_link_text("Arrangementer").click()
        WebDriverWait(self.browser, 10).until(
            lambda d: d.execute_script("return 'initialised'")
        )
        self.browser.save_screenshot("test-screens/activities_list.png")

        # Check that the page contains all activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertIn(self.activity_arrangement.name, activity_names)
        self.assertIn(self.activity_forløb.name, activity_names)
        self.assertNotIn(self.activity_foreningsmedlemskab.name, activity_names)
        self.assertNotIn(self.activity_støttemedlemskab.name, activity_names)

    def test_membership(self):
        email = "some_email@bob.gl"
        password = "MySecret"
        volunteer = VolunteerFactory.create(
            person=PersonFactory.create(
                birthday=Faker("date_between", start_date="-50y", end_date="-10y"),
                user=UserFactory.create(username=email, email=email, password=password),
            )
        )
        volunteer.person.user.set_password(password)
        volunteer.person.user.save()
        volunteer.person.birthday = datetime.date(1980, 1, 10)

        # Login
        self.browser.get(f"{self.live_server_url}/account/login")
        self.browser.save_screenshot("test-screens/login.png")
        field = self.browser.find_element_by_name("username")
        field.send_keys(email)
        field = self.browser.find_element_by_name("password")
        field.send_keys(password)

        self.browser.save_screenshot("test-screens/membership_login_filled.png")

        self.browser.find_element_by_xpath("//input[@value='Log ind']").click()
        self.browser.save_screenshot("test-screens/membership_logged_in.png")
        self.assertIn(
            "Jeres familie",
            [
                e.text
                for e in self.browser.find_elements_by_xpath(
                    "//body/descendant-or-self::*"
                )
            ],
        )

        # Loads the members
        self.browser.find_element_by_link_text("Medlemskaber").click()
        WebDriverWait(self.browser, 10).until(
            lambda d: d.execute_script("return 'initialised'")
        )
        self.browser.save_screenshot("test-screens/membership_list.png")

        # Check that the page contains all activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertNotIn(self.activity_arrangement.name, activity_names)
        self.assertNotIn(self.activity_forløb.name, activity_names)
        self.assertIn(self.activity_foreningsmedlemskab.name, activity_names)
        self.assertNotIn(self.activity_støttemedlemskab.name, activity_names)

    def test_supportmembership(self):
        email = "some_email@bob.gl"
        password = "MySecret"
        volunteer = VolunteerFactory.create(
            person=PersonFactory.create(
                birthday=Faker("date_between", start_date="-50y", end_date="-10y"),
                user=UserFactory.create(username=email, email=email, password=password),
            )
        )
        volunteer.person.user.set_password(password)
        volunteer.person.user.save()
        volunteer.person.birthday = datetime.date(1980, 1, 10)

        # Login
        self.browser.get(f"{self.live_server_url}/account/login")
        self.browser.save_screenshot("test-screens/login.png")
        field = self.browser.find_element_by_name("username")
        field.send_keys(email)
        field = self.browser.find_element_by_name("password")
        field.send_keys(password)

        self.browser.save_screenshot("test-screens/supportmembership_login_filled.png")

        self.browser.find_element_by_xpath("//input[@value='Log ind']").click()
        self.browser.save_screenshot("test-screens/supportmembership_logged_in.png")
        self.assertIn(
            "Jeres familie",
            [
                e.text
                for e in self.browser.find_elements_by_xpath(
                    "//body/descendant-or-self::*"
                )
            ],
        )

        # Loads the members
        self.browser.find_element_by_link_text("Støttemedlemskaber").click()
        WebDriverWait(self.browser, 10).until(
            lambda d: d.execute_script("return 'initialised'")
        )
        self.browser.save_screenshot("test-screens/supportmembership_list.png")

        # Check that the page contains all activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertNotIn(self.activity_arrangement.name, activity_names)
        self.assertNotIn(self.activity_forløb.name, activity_names)
        self.assertNotIn(self.activity_foreningsmedlemskab.name, activity_names)
        self.assertIn(self.activity_støttemedlemskab.name, activity_names)
