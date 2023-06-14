import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from members.tests.factories import DepartmentFactory
from django.utils import timezone
from datetime import timedelta

"""
This test goes to the root signup page and creates a child and parent.
It uses the address Autocomplete widget to fill the address.

Once the form is filled it uses the generated password and checks that it can be
used to log in.
"""


class DepartmentListTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.department_1 = DepartmentFactory.create(
            created=(timezone.now() - timedelta(days=5)).date(),
            isVisible=True,
            closed_dtm=None,
        )
        self.department_1.address.region = "Region Hovedstaden"
        self.department_1.address.save()
        self.department_3 = DepartmentFactory.create(
            created=(timezone.now() - timedelta(days=5)).date(),
            isVisible=False,
            closed_dtm=None,
        )
        self.department_3.address.region = "Region Hovedstaden"
        self.department_3.address.save()
        self.department_2 = DepartmentFactory.create(
            created=(timezone.now() - timedelta(days=5)).date(),
            isVisible=True,
            closed_dtm=None,
        )
        self.department_2.address.region = "Region Syddanmark"
        self.department_2.address.save()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/department_list_final.png")
        self.browser.quit()

    def test_department_list(self):
        # Loads the departments list
        self.browser.get(f"{self.live_server_url}/departments")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/department_list_1.png")

        self.assertEquals(0, len(self.browser.find_elements(By.TAG_NAME, "nav")))
        # check that there's the "Hovedstaden" region tab
        self.browser.find_element(
            By.XPATH,
            "//div[@class='tabs']/ul/li[text()[contains(.,'Region Hovedstaden')]]",
        ).click()
        self.browser.save_screenshot("test-screens/department_list_first_region.png")

        # check that the department we made in the "Hovedstaden" region is present
        department_name = self.browser.find_element(
            By.XPATH, "//section[@id='department-container']/div/ul/li/a"
        ).get_attribute("text")
        self.assertEqual(department_name, self.department_1.name)

        # check there is only one department preset
        self.assertEqual(
            len(
                self.browser.find_elements(
                    By.XPATH, "(//section[@id='department-container'])[1]/div"
                )
            ),
            1,
        )

        # check that there's the "Syddanmark" region tab
        self.browser.find_element(
            By.XPATH,
            "//div[@class='tabs']/ul/li[text()[contains(.,'Region Syddanmark')]]",
        ).click()
        self.browser.save_screenshot("test-screens/department_list_second_region.png")
