import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from members.tests.factories import ActivityFactory
from django.utils import timezone
from datetime import timedelta


class ActivitiesListTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.activity_1 = ActivityFactory.create(
            name="Test Aktivitet",
            signup_closing=(timezone.now() + timedelta(days=5)).date(),
        )
        self.activity_1.save()
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/activities_list_final.png")
        self.browser.quit()

    def test_activities_list(self):
        # Loads the activities list
        self.browser.get(f"{self.live_server_url}/activities")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/activities_list_1.png")

        # check that the test activity is present
        activity_name = self.browser.find_element(
            By.XPATH,
            "//section[@id='current_activities']/table/tbody/tr[1]/td[@data-label='Aktivitet']",
        ).get_attribute("textContent")
        self.assertEqual(activity_name, self.activity_1.name)

        # check there is only one activity present
        self.assertEqual(
            len(
                self.browser.find_elements(
                    By.XPATH, "//section[@id='current_activities']/table/tbody"
                )
            ),
            1,
        )
