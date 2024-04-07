import os
import socket
import codecs

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from factory import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By

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
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")

        self.open_department = DepartmentFactory.create(
            name="Åben afdeling", closed_dtm=None
        )
        self.closed_department = DepartmentFactory.create(
            name="Lukket afdeling", closed_dtm=Faker("past_datetime")
        )

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )
        self.browser.save_screenshot("test-screens/volunteer_start.png")

    def tearDown(self):
        self.browser.save_screenshot("test-screens/volunteer_final.png")
        self.browser.quit()

    def test_volunteer_signup(self):
        self.browser.get(f"{self.live_server_url}/volunteer")

        options_texts = [
            e.text
            for e in self.browser.find_elements(
                By.XPATH, "//*/select[@id='id_volunteer_department']/option"
            )
        ]
        # Save HTML file
        filename = os.path.join("test-screens", "volunteer.html")
        filestream = codecs.open(filename, "w", "utf-8")
        filehandle = self.browser.page_source
        filestream.write(filehandle)

        self.assertIn(
            "Åben afdeling",
            options_texts,
        )
        self.assertNotIn(
            "Lukket afdeling",
            options_texts,
        )
