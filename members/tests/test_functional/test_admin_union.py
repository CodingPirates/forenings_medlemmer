import os
import socket
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from members.models import Union, Address, Person, Family
from members.admin.union_admin import generate_union_csv


def get_select_element_by_onchange(browser, index):
    select_elements = browser.find_elements(
        By.XPATH,
        '//select[@onchange="go_from_select(this.options[this.selectedIndex].value)"]',
    )
    return select_elements[index]


class UnionAdminTest(StaticLiveServerTestCase):
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
        self.union1 = Union.objects.create(
            name="Union1",
            address=self.address1,
            email="union1@example.com",
            founded_at="2023-01-01",
            closed_at="2023-12-31",
        )
        self.union2 = Union.objects.create(
            name="Union2",
            address=self.address2,
            email="union2@example.com",
            founded_at="2023-02-01",
            closed_at="2023-11-30",
        )
        self.family = Family.objects.create()
        self.user1 = User.objects.create_user(
            username="user1", password="password", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password", email="user2@example.com"
        )
        self.user3 = User.objects.create_user(
            username="user3", password="password", email="user3@example.com"
        )
        self.user4 = User.objects.create_user(
            username="user4", password="password", email="user4@example.com"
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
        self.person3 = Person.objects.create(
            name="person3",
            family=self.family,
            user=self.user3,
            zipcode="9101",
            city="City 3",
            streetname="Street 3",
            housenumber="3",
            floor="3",
            door="3",
            dawa_id="3",
            placename="Place 3",
            email="person3@example.com",
            phone="11223344",
            birthday="2000-03-03",
            gender="M",
        )
        self.person4 = Person.objects.create(
            name="person4",
            family=self.family,
            user=self.user4,
            zipcode="1121",
            city="City 4",
            streetname="Street 4",
            housenumber="4",
            floor="4",
            door="4",
            dawa_id="4",
            placename="Place 4",
            email="person4@example.com",
            phone="44332211",
            birthday="2000-04-04",
            gender="F",
        )

        self.union1.chairman = self.person1
        self.union1.second_chair = self.person2
        self.union1.cashier = self.person3
        self.union1.secretary = self.person4
        self.union1.save()

        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")

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

        # Navigate to the Union admin page
        self.browser.find_element(By.LINK_TEXT, "Foreninger").click()
        self.save_screenshot_and_html("union_page")

        # Test the region filter - search for Hovedstaden
        select_element = get_select_element_by_onchange(self.browser, 0)
        select = Select(select_element)
        select.select_by_visible_text("Hovedstaden")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_region_hovedstaden")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("Union1", rows[0].text)

        # Reset filter by navigating back to the main page
        self.browser.find_element(By.LINK_TEXT, "Foreninger").click()

        # Test the region filter - search for Sjælland
        select_element = get_select_element_by_onchange(self.browser, 0)
        select = Select(select_element)
        select.select_by_visible_text("Sjælland")
        self.browser.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.save_screenshot_and_html("filter_region_sjælland")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("Union2", rows[0].text)

        # Reset filter by navigating back to the main page
        self.browser.find_element(By.LINK_TEXT, "Foreninger").click()

        # Test the search field for "Union1"
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.send_keys("Union1")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_union_1")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("Union1", rows[0].text)

        # Reset filter by navigating back to the main page
        self.browser.find_element(By.LINK_TEXT, "Foreninger").click()

        # Test the search field for "1234" (zipcode of address1)
        search_input = self.browser.find_element(By.NAME, "q")
        search_input.clear()
        search_input.send_keys("1234")
        search_input.send_keys(Keys.RETURN)
        self.save_screenshot_and_html("search_zipcode_1234")
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#result_list tbody tr")
        self.assertEqual(len(rows), 1)
        self.assertIn("Union1", rows[0].text)

        # Reset filter by navigating back to the main page
        self.browser.find_element(By.LINK_TEXT, "Foreninger").click()

    def test_generate_union_csv(self):
        # test the "Exporter Foreningsinformationer" action
        queryset = Union.objects.all()
        result_string = generate_union_csv(queryset)
        expected_csv_content = (
            "Forening;Email;Oprettelsdato;Lukkedato;"
            "formand-navn;formand-email;formand-tlf;"
            "næstformand-navn;næstformand-email;næstformand-tlf;"
            "kasserer-navn;kasserer-email;kasserer-tlf;"
            "sekretær-navn;sekretær-email;sekretær-tlf\n"
            "Union1;union1@example.com;2023-01-01;2023-12-31;"
            "person1;person1@example.com;12345678;"
            "person2;person2@example.com;87654321;"
            "person3;person3@example.com;11223344;"
            "person4;person4@example.com;44332211\n"
            "Union2;union2@example.com;2023-02-01;2023-11-30;"
            ";;;;;;;;;;;\n"
        )

        self.assertEqual(result_string, expected_csv_content)
