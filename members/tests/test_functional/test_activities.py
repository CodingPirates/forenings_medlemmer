import datetime
import os
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from factory import Faker
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait

from members.tests.factories import (
    ActivityFactory,
    PersonFactory,
    ActivityParticipantFactory,
    MemberFactory,
)
from members.tests.factories.person_factory import UserFactory

"""
This test goes to the activities list.
"""


class ActivitiesTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.email = "some_email@bob.gl"
        self.password = "MySecret"
        self.member = MemberFactory.create(
            person=PersonFactory.create(
                birthday=Faker("date_between", start_date="-50y", end_date="-10y"),
                user=UserFactory.create(
                    username=self.email, email=self.email, password=self.password
                ),
            )
        )
        self.member.person.user.set_password(self.password)
        self.member.person.user.save()
        self.member.person.birthday = datetime.date(1980, 1, 10)

        self.activity_arrangement = ActivityFactory.create(
            open_invite=True,
            signup_closing=Faker("future_datetime", end_date="+100d"),
            min_age=5,
            max_age=90,
            name="Arrangement",
            activitytype_id="ARRANGEMENT",
        )
        self.activity_arrangement.save()
        self.activity_arrangement_participate = ActivityFactory.create(
            name="Arrangement deltagelse", activitytype_id="ARRANGEMENT"
        )
        self.activity_arrangement_participate.save()
        ActivityParticipantFactory.create(
            activity=self.activity_arrangement_participate, member=self.member
        ).save()
        self.activity_forløb = ActivityFactory.create(
            open_invite=True,
            signup_closing=Faker("future_datetime", end_date="+100d"),
            min_age=5,
            max_age=90,
            name="Forløb",
            activitytype_id="FORLØB",
        )
        self.activity_forløb.save()
        self.activity_forløb_participate = ActivityFactory.create(
            name="Forløb deltagelse", activitytype_id="FORLØB"
        )
        self.activity_forløb_participate.save()
        ActivityParticipantFactory.create(
            activity=self.activity_forløb_participate, member=self.member
        ).save()
        self.activity_foreningsmedlemskab = ActivityFactory.create(
            open_invite=True,
            signup_closing=Faker("future_datetime", end_date="+100d"),
            min_age=5,
            max_age=90,
            name="Foreningsmedlemskab",
            activitytype_id="FORENINGSMEDLEMSKAB",
        )
        self.activity_foreningsmedlemskab.save()
        self.activity_foreningsmedlemskab_participate = ActivityFactory.create(
            name="Foreningsmedlemskab deltagelse", activitytype_id="FORENINGSMEDLEMSKAB"
        )
        self.activity_foreningsmedlemskab_participate.save()
        ActivityParticipantFactory.create(
            activity=self.activity_foreningsmedlemskab_participate, member=self.member
        ).save()
        self.activity_støttemedlemskab = ActivityFactory.create(
            open_invite=True,
            signup_closing=Faker("future_datetime", end_date="+100d"),
            min_age=5,
            max_age=90,
            name="Støttemedlemskab",
            activitytype_id="STØTTEMEDLEMSKAB",
        )
        self.activity_støttemedlemskab.save()
        self.activity_støttemedlemskab_participate = ActivityFactory.create(
            name="Støttemedlemskab deltagelse", activitytype_id="STØTTEMEDLEMSKAB"
        )
        self.activity_støttemedlemskab_participate.save()
        ActivityParticipantFactory.create(
            activity=self.activity_støttemedlemskab_participate, member=self.member
        ).save()

        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

        # Login
        self.browser.get(f"{self.live_server_url}/account/login")
        self.browser.save_screenshot("test-screens/login.png")
        field = self.browser.find_element_by_name("username")
        field.send_keys(self.email)
        field = self.browser.find_element_by_name("password")
        field.send_keys(self.password)

        self.browser.save_screenshot("test-screens/activities_login_filled.png")

        self.browser.find_element_by_xpath("//input[@value='Log ind']").click()
        self.browser.save_screenshot("test-screens/activities_logged_in.png")

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/activities_list_final.png")
        self.browser.quit()

    def test_entry_page(self):
        self.assertIn(
            "Jeres familie",
            [
                e.text
                for e in self.browser.find_elements_by_xpath(
                    "//body/descendant-or-self::*"
                )
            ],
        )
        self.browser.find_element_by_link_text("Se familie")
        self.browser.find_element_by_link_text("Afdelinger")
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Arrangementer"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Medlemskaber"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Støttemedlemskaber"),
            )
        )
        self.assertEqual(links[0], links[1])

    def test_activities(self):

        # Loads the activities
        self.browser.find_element_by_link_text("Arrangementer").click()
        WebDriverWait(self.browser, 10).until(
            lambda d: d.execute_script("return 'initialised'")
        )
        self.browser.save_screenshot("test-screens/activities_list.png")

        # Check that the page contains all participating activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//section[@id='participation']/table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertEqual(2, len(activity_names))
        self.assertIn(self.activity_arrangement_participate.name, activity_names)
        self.assertIn(self.activity_forløb_participate.name, activity_names)

        # Check that the page contains all activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//section[@id='open_activities']/table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertEqual(2, len(activity_names))
        self.assertIn(self.activity_arrangement.name, activity_names)
        self.assertIn(self.activity_forløb.name, activity_names)

    def test_membership(self):
        # Loads the members
        self.browser.find_element_by_link_text("Medlemskaber").click()
        WebDriverWait(self.browser, 10).until(
            lambda d: d.execute_script("return 'initialised'")
        )
        self.browser.save_screenshot("test-screens/membership_list.png")

        # Check that the page contains all participating activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//section[@id='participation']/table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertEqual(1, len(activity_names))
        self.assertIn(
            self.activity_foreningsmedlemskab_participate.name, activity_names
        )

        # Check that the page contains all activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//section[@id='open_activities']/table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertEqual(1, len(activity_names))
        self.assertIn(self.activity_foreningsmedlemskab.name, activity_names)

    def test_supportmembership(self):
        # Loads the members
        self.browser.find_element_by_link_text("Støttemedlemskaber").click()
        WebDriverWait(self.browser, 10).until(
            lambda d: d.execute_script("return 'initialised'")
        )
        self.browser.save_screenshot("test-screens/supportmembership_list.png")

        # Check that the page contains all participating activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//section[@id='participation']/table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertEqual(1, len(activity_names))
        self.assertIn(self.activity_støttemedlemskab_participate.name, activity_names)

        # Check that the page contains all activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//section[@id='open_activities']/table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertEqual(1, len(activity_names))
        self.assertIn(self.activity_støttemedlemskab.name, activity_names)
