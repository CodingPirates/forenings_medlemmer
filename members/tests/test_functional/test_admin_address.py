import os
import socket
from datetime import date

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from forenings_medlemmer.settings import MINIMUM_SEASON_PRICE_IN_DKK
from members.models import (
    Activity,
    ActivityType,
    Address,
    Department,
    Union,
)
from members.tests.test_functional.helpers import complete_admin_signup


class AddressAdminTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )

        self.address1 = Address.objects.create(
            streetname="Street 1",
            housenumber="1",
            city="City 1",
            zipcode="1234",
            region="Region Hovedstaden",
            descriptiontext="Original description",
        )
        self.union = Union.objects.create(name="Union1", address=self.address1)
        self.department = Department.objects.create(
            name="Department1", address=self.address1, union=self.union, isVisible=True
        )

        self.activity_type, created = ActivityType.objects.get_or_create(
            id="FORLØB",
            defaults={"display_name": "Forløb", "description": "Forløb description"},
        )
        self.activity = Activity.objects.create(
            name="Activity1",
            department=self.department,
            activitytype=self.activity_type,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 1),
            address=self.address1,
            season_fee=MINIMUM_SEASON_PRICE_IN_DKK + 1,
        )

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )

        if not os.path.exists("test-screens"):
            os.makedirs("test-screens")

    def wait_for_element(self, by, value, timeout=10):
        return WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_address_description(self, expected_value, timeout=10):
        return WebDriverWait(self.browser, timeout).until(
            lambda _browser: Address.objects.get(pk=self.address1.pk).descriptiontext
            == expected_value
        )

    def get_admin_feedback(self):
        selectors = [
            ".errornote",
            ".errorlist li",
            ".messagelist li",
            ".messagelist .success",
            ".messagelist .warning",
            ".messagelist .error",
        ]
        messages = []
        for selector in selectors:
            for element in self.browser.find_elements(By.CSS_SELECTOR, selector):
                text = element.text.strip()
                if text and text not in messages:
                    messages.append(text)
        return messages

    def tearDown(self):
        self.browser.quit()

    def save_screenshot_and_html(self, name):
        self.browser.save_screenshot(f"test-screens/{name}.png")
        with open(f"test-screens/{name}.html", "w") as f:
            f.write(self.browser.page_source)

    def test_admin_change_address_description(self):
        # Log in to the admin site
        self.browser.get(f"{self.live_server_url}/admin/")
        username_input = self.wait_for_element(By.NAME, "username")
        password_input = self.wait_for_element(By.NAME, "password")
        username_input.send_keys("admin")
        password_input.send_keys("password")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("address_admin_login")

        # A new admin user must complete the signup flow before the admin works
        complete_admin_signup(self, self.browser, self.department)

        # Now that the admin has a person, the admin interface can be loaded
        self.browser.get(f"{self.live_server_url}/admin/")
        self.wait_for_element(By.TAG_NAME, "body")

        # Open the address change page using its stable admin URL
        self.browser.get(
            f"{self.live_server_url}{reverse('admin:members_address_change', args=[self.address1.pk])}"
        )
        self.assertNotIn(
            "/admin/login/",
            self.browser.current_url,
            f"Admin user was redirected back to login, current URL: {self.browser.current_url}",
        )
        self.wait_for_element(By.ID, "id_descriptiontext")
        self.save_screenshot_and_html("address_admin_change_form")

        # Change the description text and save
        description_input = self.wait_for_element(By.ID, "id_descriptiontext")
        description_input.clear()
        description_input.send_keys("Updated description")
        self.browser.find_element(By.NAME, "_save").click()
        WebDriverWait(self.browser, 10).until(EC.staleness_of(description_input))
        self.wait_for_element(By.TAG_NAME, "body")
        self.save_screenshot_and_html("address_admin_after_save")
        try:
            self.wait_for_address_description("Updated description")
        except TimeoutException:
            self.address1.refresh_from_db()
            feedback = self.get_admin_feedback()
            feedback_text = (
                " | ".join(feedback)
                if feedback
                else "Ingen synlige admin-beskeder fundet"
            )
            self.fail(
                "Address description was not saved. "
                f"Current URL: {self.browser.current_url}. "
                f"DB value: {self.address1.descriptiontext!r}. "
                f"Admin feedback: {feedback_text}"
            )

        # The change should succeed and the updated value should be persisted
        self.assertNotIn(
            "Server Error",
            self.browser.page_source,
            f"Saving the address failed: {self.browser.page_source}",
        )
        self.assertNotIn(
            "/admin/login/",
            self.browser.current_url,
            f"Admin user was redirected back to login after saving, current URL: {self.browser.current_url}",
        )
        self.address1.refresh_from_db()
        self.assertEqual(self.address1.descriptiontext, "Updated description")
