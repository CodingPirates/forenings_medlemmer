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
        self.browser.save_screenshot("test-screens/membership_test_final.png")
        self.browser.quit()

    def test_entry_page(self):
        log_in(self, self.person)

        get_text_contains(self.browser, "få medlemsskab")[0].click()

        self.assertGreater(
            len(get_text_contains(self.browser, "Mine medlemsskaber")), 0
        )

        # Check row in membership table has kid name it has the name
        self.assertEqual(self.browser.find_element_by_xpath("//td").text, str(self.kid))
