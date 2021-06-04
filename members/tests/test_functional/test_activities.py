import os
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from factory import Faker
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait

from members.tests.factories import (
    ActivityFactory,
    ActivityParticipantFactory,
    MemberFactory,
)
from members.tests.test_functional.functional_helpers import log_in

"""
This test goes to the activities list.
"""


class ActivitiesTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.member = MemberFactory.create()

        self.activities = {}
        for activity_type in [
            "ARRANGEMENT",
            "FORLØB",
            "FORENINGSMEDLEMSKAB",
            "STØTTEMEDLEMSKAB",
        ]:
            self.activities[activity_type] = {}
            for variant in ["participate", "recent", "old"]:
                self.activities[activity_type][variant] = ActivityFactory.create(
                    open_invite=True,
                    min_age=5,
                    max_age=90,
                    signup_closing=(
                        Faker("past_date", start_date="-10d")
                        if variant == "old"
                        else Faker("future_datetime", end_date="+100d")
                    ),
                    name=f"-{activity_type}-{variant}",
                    activitytype_id=activity_type,
                )
                if variant == "participate":
                    ActivityParticipantFactory.create(
                        activity=self.activities[activity_type][variant],
                        member=self.member,
                    )

        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

        # Login
        log_in(self, self.member.person)

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
        self.assertIn(
            self.activities["ARRANGEMENT"]["participate"].name, activity_names
        )
        self.assertIn(self.activities["FORLØB"]["participate"].name, activity_names)

        # Check that the page contains all activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//section[@id='open_activities']/table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertEqual(2, len(activity_names))
        self.assertIn(self.activities["ARRANGEMENT"]["recent"].name, activity_names)
        self.assertIn(self.activities["FORLØB"]["recent"].name, activity_names)

    def test_membership(self):
        # Loads the members
        self.browser.find_element_by_link_text("Medlemskaber").click()
        WebDriverWait(self.browser, 10).until(
            lambda d: d.execute_script("return 'initialised'")
        )
        self.browser.save_screenshot("test-screens/membership_list.png")

        # Check that the page contains all participating activities
        activities = self.browser.find_elements_by_xpath(
            "//section[@id='participation']/table/tbody/tr"
        )
        self.assertEqual(1, len(activities))
        self.assertEqual(
            self.activities["FORENINGSMEDLEMSKAB"]["participate"].name,
            activities[0].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities["FORENINGSMEDLEMSKAB"]["participate"].union.name,
            activities[0].find_element_by_xpath("td[@data-label='Forening']").text,
        )

        # Check that the page contains all activities
        activities = self.browser.find_elements_by_xpath(
            "//section[@id='open_activities']/table/tbody/tr"
        )
        self.assertEqual(1, len(activities))
        self.assertEqual(
            self.activities["FORENINGSMEDLEMSKAB"]["recent"].name,
            activities[0].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities["FORENINGSMEDLEMSKAB"]["recent"].union.name,
            activities[0].find_element_by_xpath("td[@data-label='Forening']").text,
        )

    def test_supportmembership(self):
        # Loads the members
        self.browser.find_element_by_link_text("Støttemedlemskaber").click()
        WebDriverWait(self.browser, 10).until(
            lambda d: d.execute_script("return 'initialised'")
        )
        self.browser.save_screenshot("test-screens/supportmembership_list.png")

        # Check that the page contains all participating activities
        activities = self.browser.find_elements_by_xpath(
            "//section[@id='participation']/table/tbody/tr"
        )
        self.assertEqual(1, len(activities))
        self.assertEqual(
            self.activities["STØTTEMEDLEMSKAB"]["participate"].name,
            activities[0].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities["STØTTEMEDLEMSKAB"]["participate"].union.name,
            activities[0].find_element_by_xpath("td[@data-label='Forening']").text,
        )

        # Check that the page contains all activities
        activities = self.browser.find_elements_by_xpath(
            "//section[@id='open_activities']/table/tbody/tr"
        )
        self.assertEqual(1, len(activities))
        self.assertEqual(
            self.activities["STØTTEMEDLEMSKAB"]["recent"].name,
            activities[0].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities["STØTTEMEDLEMSKAB"]["recent"].union.name,
            activities[0].find_element_by_xpath("td[@data-label='Forening']").text,
        )
