import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from members.tests.factories import PersonFactory, FamilyFactory, UnionFactory
from members.models import Membership
from datetime import date
from .functional_helpers import log_in, get_text_contains

"""
This test starts with a family with a child that is a member and the parent
wants to become a member.

The parent ques to quickpay and leaves the page without entering card details.
Once they go back to our page it is marked at not payed.
"""


class SignUpTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())

    def setUp(self):
        self.email = "parent@example.com"
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )
        self.family = FamilyFactory()
        self.person = PersonFactory.create(family=self.family)
        self.kid = PersonFactory.create(family=self.family, membertype="CH")
        self.union = UnionFactory.create()
        Membership.objects.create(
            union=self.union, person=self.kid, sign_up_date=date.today()
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/membership_test_final_not_payed.png")
        self.browser.quit()

    def test_entry_page(self):
        log_in(self, self.person)

        get_text_contains(self.browser, "få medlemsskab")[0].click()
        # Check row in membership table has kid's name in it

        self.browser.find_element_by_name("person").click()

        # Click on option in select that has parent name
        self.browser.find_element_by_xpath(
            f"//*[@id='id_person']/option[text()[contains(., '{self.person}')]]"
        ).click()

        # Click on select Union
        self.browser.find_element_by_name("union").click()
        self.browser.find_element_by_xpath(
            f"//*[@id='id_union']/option[text()[contains(., '{self.union}')]]"
        ).click()

        # Gå til betaling
        self.browser.find_element_by_xpath("//input[@type='submit']").click()

        # Leave quickpay and go back to entry page
        self.browser.get(f"{self.live_server_url}")

        # Go to paymetns views
        get_text_contains(self.browser, "Se dine betalinger")[0].click()

        # Klick "ikke betalt" button
        self.browser.find_element_by_class_name("button-danger").click()

        # Back at quickpay
        self.assertIn("https://payment.quickpay.net", self.browser.current_url)
