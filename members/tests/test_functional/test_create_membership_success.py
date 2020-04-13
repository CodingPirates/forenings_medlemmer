import os
import socket
from datetime import date
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from members.models import Membership, PayableItem
from members.tests.factories import FamilyFactory, PersonFactory, UnionFactory

from .functional_helpers import get_text_contains, log_in


"""
This test starts with a family with a child that is a member and the parent
wants to become a member.

The parent ques to quickpay and enters a valid card, is sent to the payments
screen. And recvies an email confirmation.
"""


class SignUpTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    # TODO save screenshost along the way

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
        # Check row in membership table has kid's name in it
        self.assertEqual(self.browser.find_element_by_xpath("//td").text, str(self.kid))
        self.assertGreater(
            len(get_text_contains(self.browser, "Mine medlemsskaber")), 0
        )

        # Click on select person
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

        try:  # Wait to be redirected to quickpay, worst case i 5 mins
            WebDriverWait(self.browser, 60).until(
                EC.title_is("Coding Pirates Test Account")
            )
        except Exception:
            self.fail("Was not sent to quickpay")

        # Enter card number
        card_field = self.browser.find_element_by_id("cardnumber")
        card_field.send_keys(Keys.NUMPAD1)
        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD0)

        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD6)
        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD0)

        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD0)

        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD0)
        card_field.send_keys(Keys.NUMPAD2)
        # self.browser.find_element_by_id("cardnumber").send_keys("1000 0600 0000 0002")
        time.sleep(1)

        # Enter experation month
        self.browser.find_element_by_id("expiration-month").send_keys("11")

        # Enter experation year
        self.browser.find_element_by_id("expiration-year").send_keys("30")

        # Enter CVS
        self.browser.find_element_by_id("cvd").send_keys("208")
        self.browser.find_element_by_id("cvd").send_keys(Keys.TAB)

        self.browser.save_screenshot("test-screens/membership_test_card_details.png")

        # Finish payment
        self.browser.find_element_by_xpath("//*[@type='submit']").click()

        try:  # Wait to be redirected back from quickpay, worst case i 5 mins
            WebDriverWait(self.browser, 60).until(
                EC.title_is("Coding Pirates Medlemssystem")
            )
        except Exception:
            self.fail("Was not sent back to own page")

        payment_statuses = self.browser.find_elements_by_xpath(
            '//*/td[@data-label="Status"]'
        )
        for status in payment_statuses:
            self.assertEqual(status.text.strip(), "Betalt")

        # Sent one confirmation email
        self.assertEqual(PayableItem.send_all_payment_confirmations(), [1])

        # Check that we can't send it again
        self.assertEqual(PayableItem.send_all_payment_confirmations(), [])

        # Sent to right person
        self.assertEqual(mail.outbox[0].to, [self.person.email])
