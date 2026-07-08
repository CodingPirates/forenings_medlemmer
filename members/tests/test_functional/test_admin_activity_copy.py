import os
import socket
from datetime import date

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .helpers import complete_admin_signup

# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select
from members.models import (
    Activity,
    ActivityType,
    Address,
    Department,
    Family,
    Person,
    Union,
)


class AdminActivityCopyTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )

        self.client.login(username="admin", password="password")

        self.address1 = Address.objects.create(
            streetname="Street 1",
            city="City 1",
            zipcode="1234",
            region="Region Hovedstaden",
        )
        self.address2 = Address.objects.create(
            streetname="Street 2",
            city="City 2",
            zipcode="5678",
            region="Region Sjælland",
        )
        self.union = Union.objects.create(name="Union1", address=self.address1)
        self.family = Family.objects.create()
        self.user1 = User.objects.create_user(
            username="user1", password="password", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password", email="user2@example.com"
        )
        self.person1 = Person.objects.create(
            name="person1",
            family=self.family,
            user=self.user1,
            zipcode="1234",
            city="City 1",
            streetname="Street 1",
            housenumber="1",
            floor="1",
            door="1",
            dawa_id="1",
            placename="Place 1",
            email="person1@example.com",
            phone="12345678",
            birthday="2000-01-01",
            gender="M",
        )
        self.person2 = Person.objects.create(
            name="person2",
            family=self.family,
            user=self.user2,
            zipcode="5678",
            city="City 2",
            streetname="Street 2",
            housenumber="2",
            floor="2",
            door="2",
            dawa_id="2",
            placename="Place 2",
            email="person2@example.com",
            phone="87654321",
            birthday="2000-02-02",
            gender="F",
        )
        self.department1 = Department.objects.create(
            name="Department1", address=self.address1, union=self.union, isVisible=True
        )
        self.department2 = Department.objects.create(
            name="Department2", address=self.address2, union=self.union, isVisible=False
        )
        self.department1.department_leaders.add(self.person1)
        self.department2.department_leaders.add(self.person2)

        # Create records for the four different activity types if they don't already exist
        self.activity_type1, created = ActivityType.objects.get_or_create(
            id="FORLØB",
            defaults={"display_name": "Forløb", "description": "Forløb description"},
        )
        self.activity_type2, created = ActivityType.objects.get_or_create(
            id="ARRANGEMENT",
            defaults={
                "display_name": "Arrangement",
                "description": "Arrangement description",
            },
        )
        self.activity_type3, created = ActivityType.objects.get_or_create(
            id="FORENINGSMEDLEMSKAB",
            defaults={
                "display_name": "Foreningsmedlemskab",
                "description": "Foreningsmedlemskab description",
            },
        )
        self.activity_type4, created = ActivityType.objects.get_or_create(
            id="STØTTEMEDLEMSKAB",
            defaults={
                "display_name": "Støttemedlemskab",
                "description": "Støttemedlemskab description",
            },
        )

        self.activity1 = Activity.objects.create(
            name="Activity1",
            department=self.department1,
            activitytype=self.activity_type1,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 1),
            address=self.address1,
        )
        self.activity2 = Activity.objects.create(
            name="Activity2",
            department=self.department1,
            activitytype=self.activity_type2,
            start_date=date(2023, 2, 1),
            end_date=date(2023, 2, 1),
            address=self.address1,
        )
        self.activity3 = Activity.objects.create(
            name="Activity3",
            department=self.department1,
            activitytype=self.activity_type3,
            start_date=date(2023, 3, 1),
            end_date=date(2023, 3, 1),
            address=self.address1,
        )
        self.activity4 = Activity.objects.create(
            name="Activity4",
            department=self.department1,
            activitytype=self.activity_type4,
            start_date=date(2023, 4, 1),
            end_date=date(2023, 4, 1),
            address=self.address1,
        )

        self.download_dir = os.path.join(os.getcwd(), "test-screens/activity")
        if not os.path.exists(self.download_dir):
            os.mkdir(self.download_dir)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )

        # Log in to the admin site
        self.browser.get(f"{self.live_server_url}/admin/")
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("admin")
        password_input.send_keys("password")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        # The admin has no person yet, so the consent middleware redirects to
        # the admin signup form, where an ordinary user must be created.
        complete_admin_signup(self, self.browser, self.department1)

    def tearDown(self):
        self.browser.quit()

    def save_screenshot_and_html(self, name):
        self.browser.save_screenshot(f"{self.download_dir}/{name}.png")
        with open(f"{self.download_dir}/{name}.html", "w") as f:
            f.write(self.browser.page_source)

    def execute_copy_activity_action(self):
        select_element = Select(
            self.browser.find_element(By.XPATH, '//select[@name="action"]')
        )
        select_element.select_by_visible_text("Kopier én aktiviet")
        self.browser.find_element(
            By.XPATH, '//*[@class="actions"]/button[@type="submit"]'
        ).click()

    # Test for warning if more than one activity is selected when pressing "Udfør" button.
    def test_error_on_multiple_activities(self):
        # Navigate to the admin interface
        self.browser.get(f"{self.live_server_url}/admin")

        # Navigate to the activity admin page
        self.browser.find_element(By.LINK_TEXT, "Aktiviteter").click()
        # self.save_screenshot_and_html("activity_page")

        # Select 2 activities.
        for position in range(1, 3):
            xpath = f'//*[@id="result_list"]/tbody/tr[{position}]/td/input[@class="action-select"]'
            self.browser.find_element(By.XPATH, xpath).click()
        # self.save_screenshot_and_html("activity_page_items_selected")

        execute_copy_activity_action(self.browser)

        try:
            expected_message = "Du må maks vælge én aktivitet af gangen til kopiering."
            WebDriverWait(self.browser, 10).until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, '//*[@class="error"]'), expected_message
                )
            )
            self.save_screenshot_and_html("expected_error_massage")
        except:
            self.save_screenshot_and_html("missing_error_massage")
            self.fail("Error message not found!")

    # Test if copied activity gets editable immediately after a successful copy.
    def test_new_copy_apperas_on_change_activity_page(self):
        # Navigate to the admin interface
        self.browser.get(f"{self.live_server_url}/admin")

        # Navigate to the activity admin page
        self.browser.find_element(By.LINK_TEXT, "Aktiviteter").click()
        # self.save_screenshot_and_html("activity_page")

        # Select 1 activity.
        xpath = f'//*[@id="result_list"]/tbody/tr[1]/td/input[@class="action-select"]'
        self.browser.find_element(By.XPATH, xpath).click()
        # self.save_screenshot_and_html("activity_page_item_selected")

        execute_copy_activity_action(self.browser)

        try:
            WebDriverWait(self.browser, 10).until(EC.url_contains("copy_activity"))
            self.browser.find_element(By.XPATH, '//*[@id="confirma_action"]').click()
        except:
            self.save_screenshot_and_html("failed_to_reach_copy_activity_page")
            self.fail("Could not reach confirmation page for copy activity!")

        try:
            WebDriverWait(self.browser, 10).until(EC.url_contains("change"))
            self.save_screenshot_and_html("change_activity_page")
        except Exception:
            self.save_screenshot_and_html("not_on_change_activity_page")
            self.fail("Failed to reach change activity page!")
