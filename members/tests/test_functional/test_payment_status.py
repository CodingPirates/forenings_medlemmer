import os
import socket
import time
from datetime import date

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.utils import override_settings
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from members.models import Payment
from members.tests.factories import ActivityFactory, FamilyFactory, PersonFactory

from .functional_helpers import get_text_contains, log_in

"""
Creates two children and pays for thir activities, the first fails the second
passes. It tests that the status of the payments are correct.
"""


class SignUpTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.email = "parent@example.com"
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )
        self.family = FamilyFactory()
        self.person = PersonFactory.create(family=self.family)
        self.first_kid = PersonFactory.create(family=self.family, membertype="CH")
        self.second_kid = PersonFactory.create(family=self.family, membertype="CH")
        self.activity = ActivityFactory.create(
            start_date=date.today(),
            signup_closing=date.today(),
            open_invite=True,
            max_participants=2,
            min_age=0,
            max_age=100,
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/payment_status.png")
        self.browser.quit()

    @override_settings(DEBUG=True)
    def test_account_create(self):
        log_in(self, self.person)

        # Goes to activity sign up screen for first kid
        self.browser.get(
            f"{self.live_server_url}/family/activity/{self.activity.id}/person/{self.first_kid.id}/"
        )

        # Accept payment_conditions
        dropdown = Select(self.browser.find_element_by_id("id_read_conditions"))
        dropdown.select_by_value("YES")

        # Accept photo_conditions
        dropdown = Select(self.browser.find_element_by_id("id_photo_permission"))
        dropdown.select_by_value("OK")

        # Click payment button and go to quickpay
        self.browser.find_element_by_id(
            "submit-id-submit"
        ).click()  # TODO Chanage Shitty id, when form is rewritten

        # Ensure we only run test on quickpay test account
        self.assertGreater(
            len(get_text_contains(self.browser, "Coding Pirates Test Account")), 0
        )

        # Leave payment page without entering card details
        # Go to activites screen for second kid
        self.browser.get(
            f"{self.live_server_url}/family/activity/{self.activity.id}/person/{self.second_kid.id}/"
        )

        # Accept payment_conditions
        dropdown = Select(self.browser.find_element_by_id("id_read_conditions"))
        dropdown.select_by_value("YES")

        # Accept photo_conditions
        dropdown = Select(self.browser.find_element_by_id("id_photo_permission"))
        dropdown.select_by_value("OK")

        # Click payment button and go to quickpay
        self.browser.find_element_by_id(
            "submit-id-submit"
        ).click()  # TODO Chanage Shitty id, when form is rewritten

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

        # Finish payment
        self.browser.find_element_by_xpath("//*[@type='submit']").click()

        # self.browser.get(f"{self.live_server_url}")
        first_kid_payment = Payment.objects.get(
            activityparticipant__member__person=self.first_kid
        )
        second_kid_payment = Payment.objects.get(
            activityparticipant__member__person=self.second_kid
        )

        first_kid_payment.get_quickpaytransaction().update_status()
        second_kid_payment.get_quickpaytransaction().update_status()

        self.assertIsNone(first_kid_payment.accepted_dtm)
        self.assertIsNone(first_kid_payment.confirmed_dtm)

        self.assertIsNotNone(second_kid_payment.accepted_dtm)
        self.assertIsNotNone(second_kid_payment.confirmed_dtm)
