import os
import socket
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from members.models import (
    WaitingList,
    Municipality,
    Person,
    Department,
    Union,
    Address,
    Family,
)


def get_select_element_by_onchange(browser, index):
    select_elements = browser.find_elements(
        By.XPATH,
        '//select[@onchange="go_from_select(this.options[this.selectedIndex].value)"]',
    )
    return select_elements[index]


class WaitingListAdminSeleniumTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        self.address = Address.objects.create(
            streetname="Street 1", city="City 1", zipcode="1234"
        )
        self.union = Union.objects.create(name="Union1", address=self.address)
        self.department = Department.objects.create(
            name="Department1", union=self.union, address=self.address
        )
        self.family = Family.objects.create()
        self.municipality1 = Municipality.objects.create(
            name="Municipality1", address="Address 1", zipcode="1234", city="City 1"
        )
        self.municipality2 = Municipality.objects.create(
            name="Municipality2", address="Address 2", zipcode="6789", city="City 2"
        )
        self.person1 = Person.objects.create(
            name="person1",
            municipality=self.municipality1,
            department=self.department,
            family=self.family,
            zipcode="2345",
            gender="MA",  # Correct gender value for male
        )
        self.person2 = Person.objects.create(
            name="person2",
            municipality=self.municipality2,
            department=self.department,
            family=self.family,
            zipcode="3456",
            gender="FM",  # Correct gender value for female
        )
        self.person3 = Person.objects.create(
            name="person3",
            municipality=None,
            department=self.department,
            family=self.family,
            gender="OT",  # Correct gender value for other
        )
        self.waiting_list1 = WaitingList.objects.create(
            person=self.person1, department=self.department
        )
        self.waiting_list2 = WaitingList.objects.create(
            person=self.person2, department=self.department
        )
        self.waiting_list3 = WaitingList.objects.create(
            person=self.person3, department=self.department
        )

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

        # Navigate to the WaitingList admin page
        self.browser.find_element(By.LINK_TEXT, "Ventelister").click()
        self.save_screenshot_and_html("waiting_list_page")

        # Test the municipality filter - search for Municipality1
        select_element = get_select_element_by_onchange(self.browser, 2)
        select = Select(select_element)
        select.select_by_visible_text("Municipality1")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_municipality_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("person1", rows[0].text)

        # Test the municipality filter - search for Municipality2
        select_element = get_select_element_by_onchange(self.browser, 2)
        select = Select(select_element)
        select.select_by_visible_text("Municipality2")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_municipality_2")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("person2", rows[0].text)

        # Test the municipality filter - search for "(Uden kommune)" and "(Med kommune)"
        select_element = get_select_element_by_onchange(self.browser, 2)
        select = Select(select_element)
        select.select_by_visible_text("(Uden kommune)")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_no_municipality")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("person3", rows[0].text)

        select_element = get_select_element_by_onchange(self.browser, 2)
        select = Select(select_element)
        select.select_by_visible_text("(Med kommune)")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_with_municipality")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 2)
        self.assertIn("person1", rows[0].text)
        self.assertIn("person2", rows[1].text)

        # Reset the municipality filter to "Alle"
        select_element = get_select_element_by_onchange(self.browser, 2)
        select = Select(select_element)
        select.select_by_visible_text("Alle")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("reset_municipality_filter")

        # Test the Union (Forening) filter
        select_element = get_select_element_by_onchange(self.browser, 0)
        select = Select(select_element)
        select.select_by_visible_text("Union1")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_union_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 3)
        self.assertIn("person1", rows[0].text)
        self.assertIn("person2", rows[1].text)
        self.assertIn("person3", rows[2].text)

        # Reset the union filter to "Alle"
        select_element = get_select_element_by_onchange(self.browser, 0)
        select = Select(select_element)
        select.select_by_visible_text("Alle")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("reset_union_filter")

        # Test the Department (Afdeling) filter
        select_element = get_select_element_by_onchange(self.browser, 1)
        select = Select(select_element)
        select.select_by_visible_text("Department1")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_department_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 3)
        self.assertIn("person1", rows[0].text)
        self.assertIn("person2", rows[1].text)
        self.assertIn("person3", rows[2].text)

        # Reset the Department filter to "Alle"
        select_element = get_select_element_by_onchange(self.browser, 1)
        select = Select(select_element)
        select.select_by_visible_text("Alle")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("reset_department_filter")

        # Test the Gender (Køn) filter
        select_element = get_select_element_by_onchange(self.browser, 3)
        select = Select(select_element)
        select.select_by_visible_text("Dreng")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_gender_male")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("person1", rows[0].text)

        select_element = get_select_element_by_onchange(self.browser, 3)
        select = Select(select_element)
        select.select_by_visible_text("Pige")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_gender_female")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("person2", rows[0].text)

        select_element = get_select_element_by_onchange(self.browser, 3)
        select = Select(select_element)
        select.select_by_visible_text("Andet")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_gender_other")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("person3", rows[0].text)

        # Reset the Department filter to "Alle"
        select_element = get_select_element_by_onchange(self.browser, 3)
        select = Select(select_element)
        select.select_by_visible_text("Alle")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("reset_gender_filter")

        # Test the search field for "person1"
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.send_keys("person1")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_person1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("person1", rows[0].text)

        # Test the search field for "Municipality1"
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.clear()
        search_input.send_keys("Municipality1")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_municipality_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("person1", rows[0].text)

        # Test the search field for "Department1"
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.clear()
        search_input.send_keys("Department1")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_department_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 3)
        self.assertIn("person1", rows[0].text)
        self.assertIn("person2", rows[1].text)
        self.assertIn("person3", rows[2].text)

        # Test the search field for "Union1"
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.clear()
        search_input.send_keys("Union1")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_union_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 3)
        self.assertIn("person1", rows[0].text)
        self.assertIn("person2", rows[1].text)
        self.assertIn("person3", rows[2].text)

        # Test the search field for "2345" (zipcode of person1)
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.clear()
        search_input.send_keys("2345")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_zipcode_2345")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("person1", rows[0].text)
