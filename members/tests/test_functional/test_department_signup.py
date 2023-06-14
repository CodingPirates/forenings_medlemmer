import socket
import os
import codecs
import time
from datetime import timedelta
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from members.tests.factories import DepartmentFactory
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/department_signup_final.png")
        self.browser.quit()

    def test_department_signup(self):
        self.browser.maximize_window()
        self.browser.get(f"{self.live_server_url}/department_signup")

        filename = os.path.join("test-screens", "department_signup.html")
        filestream = codecs.open(filename, "w", "utf-8")
        filehandle = self.browser.page_source
        filestream.write(filehandle)

        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/department_signup_1.png")
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@id='menu-tabs']/section[@id='alle-ventelister']/div[@id='region-tabs']/ul/li[@id='tab-region-hovedstaden']",
                )
            )
        )

        self.browser.save_screenshot("test-screens/department_signup_2.png")

        region_tab = self.browser.find_element(
            By.XPATH,
            "//div[@id='menu-tabs']/section[@id='alle-ventelister']/div[@id='region-tabs']/ul/li[@id='tab-region-hovedstaden']",
        )

        self.browser.execute_script("arguments[0].scrollIntoView(true);", region_tab)
        time.sleep(0.5)  # TODO: we should avoid sleeps like this!

        self.browser.save_screenshot("test-screens/department_signup_3.png")
        region_tab.click()

        self.browser.save_screenshot("test-screens/department_signup_4.png")

        # check that the department we made in the "Hovedstaden" region is present
        department_name = self.browser.find_element(
            By.XPATH, "//tbody[@id='table-body-region-hovedstaden']/tr/td"
        ).get_attribute("innerText")
        self.assertEqual(department_name, self.department_1.name)

        # check there is only one department preset
        self.assertEqual(
            len(
                self.browser.find_elements(
                    By.XPATH, "(//tbody[@class='department-tbody'])/tr"
                )
            ),
            1,
        )
