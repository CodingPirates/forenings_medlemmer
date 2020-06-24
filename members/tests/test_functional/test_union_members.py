import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from members.tests.factories import UnionFactory, PersonFactory
from django.contrib.auth.models import User


class UnionMembersTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())

    def setUp(self):
        self.union_1 = UnionFactory.create()
        self.union_1.address.region = "Region Hovedstaden"
        self.union_1.address.save()
        self.union_2 = UnionFactory.create()
        self.union_2.address.region = "Region Syddanmark"
        self.union_2.address.save()
        self.password = "Miss1337"
        self.name = "kaptajn hack"
        self.admin = User.objects.create_superuser(
            self.name, "admin@example.com", self.password
        )
        self.person = PersonFactory.create(name=self.name, user=self.admin)
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/union_members_final.png")
        self.browser.quit()

    def test_union_members(self):
        # Loads the unions list
        self.browser.get(f"{self.live_server_url}/union_overview")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/union_members_1.png")

        # Clicks into the first union
        self.browser.find_element_by_xpath("//section/div/ul/li/a").click()
        self.browser.save_screenshot("test-screens/union_members_2.png")

        # Logs in
        field = self.browser.find_element_by_name("username")
        field.send_keys(self.name)

        field = self.browser.find_element_by_name("password")
        field.send_keys(self.password)

        # Submit form
        self.browser.find_element_by_xpath("//input[@type='submit']").click()
        self.browser.save_screenshot("test-screens/union_members_3.png")

        union_founded = self.browser.find_element_by_xpath(
            "(//div[@class='tabs reverse']/ul/li)[1]"
        ).text
        self.assertEqual(int(union_founded), self.union_1.founded.year)
