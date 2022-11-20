import socket
import os
from datetime import timedelta
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from members.tests.factories import DepartmentFactory
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class DepartmentSignupTest(StaticLiveServerTestCase):
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

        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/department_signup_final.png")
        self.browser.quit()

    def test_department_signup(self):
        self.browser.get(f"{self.live_server_url}/department_signup")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/department_signup_1.png")

        # check that there's the "Hovedstaden" region tab
        self.browser.find_element(By.XPATH,
            "//div[@class='tabs']/ul/li[text()[contains(.,'Region Hovedstaden')]]"
        ).click()
        self.browser.save_screenshot("test-screens/department_signup_2.png")

        # check that the department we made in the "Hovedstaden" region is present
        department_name = self.browser.find_element(By.XPATH,
            "//tbody[@id='department-tbody']/tr/td"
        ).get_attribute("innerText")
        self.assertEqual(department_name, self.department_1.name)

        # check there is only one department preset
        self.assertEqual(
            len(
                self.browser.find_elements(By.XPATH,
                    "(//tbody[@id='department-tbody'])/tr"
                )
            ),
            1,
        )
