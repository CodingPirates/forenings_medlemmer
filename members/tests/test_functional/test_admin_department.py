import os
import socket
from datetime import date
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from members.models import (
    Department,
    Address,
    Person,
    Union,
    Family,
    Activity,
    ActivityType,
)


def get_select_element_by_onchange(browser, index):
    select_elements = browser.find_elements(
        By.XPATH,
        '//select[@onchange="go_from_select(this.options[this.selectedIndex].value)"]',
    )
    return select_elements[index]


class DepartmentAdminTest(StaticLiveServerTestCase):
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
            union=self.union,
            activitytype=self.activity_type1,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 1),
            address=self.address1,
        )
        self.activity2 = Activity.objects.create(
            name="Activity2",
            department=self.department1,
            union=self.union,
            activitytype=self.activity_type2,
            start_date=date(2023, 2, 1),
            end_date=date(2023, 2, 1),
            address=self.address1,
        )
        self.activity3 = Activity.objects.create(
            name="Activity3",
            department=self.department1,
            union=self.union,
            activitytype=self.activity_type3,
            start_date=date(2023, 3, 1),
            end_date=date(2023, 3, 1),
            address=self.address1,
        )
        self.activity4 = Activity.objects.create(
            name="Activity4",
            department=self.department1,
            union=self.union,
            activitytype=self.activity_type4,
            start_date=date(2023, 4, 1),
            end_date=date(2023, 4, 1),
            address=self.address1,
        )

        self.download_dir = os.path.join(os.getcwd(), "test-screens/csv")
        if not os.path.exists(self.download_dir):
            os.mkdir(self.download_dir)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )

        if not os.path.exists("test-screens"):
            os.makedirs("test-screens")

    def tearDown(self):
        self.browser.quit()

    def save_screenshot_and_html(self, name):
        self.browser.save_screenshot(f"test-screens/{name}.png")
        with open(f"test-screens/{name}.html", "w") as f:
            f.write(self.browser.page_source)

    def test_admin_filter_and_search(self):
        # Log in to the admin site
        self.browser.get(f"{self.live_server_url}/admin/")
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("admin")
        password_input.send_keys("password")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("login")

        # Navigate to the Department admin page
        self.browser.find_element(By.LINK_TEXT, "Afdelinger").click()
        self.save_screenshot_and_html("department_page")

        # Test the region filter - search for Hovedstaden
        select_element = get_select_element_by_onchange(self.browser, 0)
        select = Select(select_element)
        select.select_by_visible_text("Hovedstaden")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_region_hovedstaden")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(
            len(rows), 1, f"Expected 1 row, but found {len(rows)} rows. Rows: {rows}"
        )

        # Test the region filter - search for Sjælland
        self.browser.find_element(By.LINK_TEXT, "Afdelinger").click()
        select_element = get_select_element_by_onchange(self.browser, 0)
        select = Select(select_element)
        select.select_by_visible_text("Sjælland")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_region_sjælland")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("Department2", rows[0].text)

        # Test the union filter
        self.browser.find_element(By.LINK_TEXT, "Afdelinger").click()
        select_element = get_select_element_by_onchange(self.browser, 1)
        select = Select(select_element)
        select.select_by_visible_text("Union1")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_union_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 2)
        self.assertIn("Department1", rows[0].text)
        self.assertIn("Department2", rows[1].text)

        # Test the visibility filter - search for visible departments
        self.browser.find_element(By.LINK_TEXT, "Afdelinger").click()
        select_element = get_select_element_by_onchange(self.browser, 2)
        select = Select(select_element)
        select.select_by_visible_text("Ja")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_visible_yes")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("Department1", rows[0].text)

        # Test the visibility filter - search for non-visible departments
        self.browser.find_element(By.LINK_TEXT, "Afdelinger").click()
        select_element = get_select_element_by_onchange(self.browser, 2)
        select = Select(select_element)
        select.select_by_visible_text("Nej")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_visible_no")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("Department2", rows[0].text)

        # Test the search field for "Department1"
        self.browser.find_element(By.LINK_TEXT, "Afdelinger").click()
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.send_keys("Department1")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_department_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("Department1", rows[0].text)

        # Test the search field for "1234" (zipcode of address1)
        self.browser.find_element(By.LINK_TEXT, "Afdelinger").click()
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.clear()
        search_input.send_keys("1234")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_zipcode_1234")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("Department1", rows[0].text)

        # Test the search field for "Union1"
        self.browser.find_element(By.LINK_TEXT, "Afdelinger").click()
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.clear()
        search_input.send_keys("Union1")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_union_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 2)
        self.assertIn("Department1", rows[0].text)
        self.assertIn("Department2", rows[1].text)
