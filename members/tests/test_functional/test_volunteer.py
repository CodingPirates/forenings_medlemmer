import os
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from factory import Faker
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from members.tests.factories import (
    DepartmentFactory,
)

"""
This test goes to the volunteer signup.
"""


class VolunteerTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.open_department = DepartmentFactory.create(
            name="Åben afdeling", closed_dtm=None
        )
        self.closed_department = DepartmentFactory.create(
            name="Lukket afdeling", closed_dtm=Faker("past_datetime")
        )

        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/activities_list_final.png")
        self.browser.quit()

    def test_volunteer_signup(self):
        self.browser.get(f"{self.live_server_url}/volunteer")
        options_texts = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//*/select[@id='id_volunteer_department']/option"
            )
        ]
        self.assertIn(
            "Åben afdeling",
            options_texts,
        )
        self.assertNotIn(
            "Lukket afdeling",
            options_texts,
        )
