import socket
import os
import codecs
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.text import slugify
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.utils import timezone
from datetime import timedelta

from members.tests.factories import ActivityFactory, AddressFactory, DepartmentFactory
from members.models import Address


class ActivitiesListTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        test_address = AddressFactory.create(
            region=Address.REGION_CHOICES[0][0],
        )
        test_address.save()

        test_department = DepartmentFactory.create(
            name="Test Afdeling",
            created=(timezone.now() - timedelta(days=5)).date(),
            closed_dtm=None,
            address=test_address,
        )
        test_department.save()

        self.activity_1 = ActivityFactory.create(
            name="Test Aktivitet",
            max_participants=10,
            start_date=(timezone.now() - timedelta(days=5)).date(),
            end_date=(timezone.now() + timedelta(days=5)).date(),
            signup_closing=(timezone.now() + timedelta(days=5)).date(),
            department=test_department,
        )
        self.activity_1.save()

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/activities_list_final.png")
        self.browser.quit()

    def test_activities_list(self):
        self.browser.maximize_window()
        # Loads the activities list
        self.browser.get(f"{self.live_server_url}/activities")
        # Save HTML file
        filename = os.path.join("test-screens", "activities.html")
        filestream = codecs.open(filename, "w", "utf-8")
        filehandle = self.browser.page_source
        filestream.write(filehandle)

        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/activities_list_1.png")

        # click on the right button for "Nuværende og kommende aktiviteter"
        self.browser.find_element(
            By.XPATH,
            "//div[@id='tab-menu']/ul/li[@id='tab-aktiviteter']",
        ).click()
        self.browser.save_screenshot("test-screens/activities_list_2.png")

        # check that the test activity is present
        activity_name = self.browser.find_element(
            By.XPATH,
            f"//div[@id='tab-menu']/section[@id='current-activities']/div[@id='region-tabs']/section[@id='{slugify(self.activity_1.address.region)}']/table/tbody/tr[1]/td[@data-label='Aktivitet']",
        ).get_attribute("textContent")
        self.assertEqual(activity_name, self.activity_1.name)

        # check there is only one activity present
        self.assertEqual(
            len(
                self.browser.find_elements(
                    By.XPATH,
                    f"//div[@id='tab-menu']/section[@id='current-activities']/div[@id='region-tabs']/section[@id='{slugify(self.activity_1.address.region)}']/table/tbody",
                )
            ),
            1,
        )
