import socket
from datetime import date

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from members.tests.factories import MemberFactory, PersonFactory


class MemberSummaryExportTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())

    def setUp(self):
        user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        PersonFactory(user=user)
        self.member = MemberFactory(
            member_since=date(2026, 1, 1), member_until=date(2026, 12, 31)
        )
        self.client.force_login(user)
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub", options=options
        )
        self.addCleanup(self.browser.quit)
        self.browser.get(self.live_server_url + reverse("admin:login"))
        self.browser.add_cookie(
            {"name": "sessionid", "value": self.client.cookies["sessionid"].value}
        )

    def open_summary(self):
        url = (
            self.live_server_url
            + reverse("admin:members_member_changelist")
            + "?payment_status=all"
        )
        self.browser.get(url)
        self.browser.find_element(
            By.CSS_SELECTOR, f'input.action-select[value="{self.member.pk}"]'
        ).click()
        Select(self.browser.find_element(By.NAME, "action")).select_by_value(
            "export_csv_member_summary"
        )
        self.browser.find_element(By.NAME, "index").click()
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.presence_of_element_located((By.ID, "member-summary-export")))
        return url, wait

    def test_back_button_restores_selection(self):
        url, wait = self.open_summary()
        self.browser.find_element(By.ID, "back-to-members").click()
        wait.until(EC.presence_of_element_located((By.ID, "result_list")))
        self.assertEqual(self.browser.current_url, url)
        self.assertTrue(
            self.browser.find_element(
                By.CSS_SELECTOR, f'input.action-select[value="{self.member.pk}"]'
            ).is_selected()
        )

    def test_download_returns_to_filtered_member_list(self):
        url, wait = self.open_summary()
        self.browser.execute_script("""
            const originalFetch = window.fetch;
            window.fetch = async (...args) => {
                const response = await originalFetch(...args);
                sessionStorage.setItem("summaryCsv", await response.clone().text());
                return response;
            };
            const originalClick = HTMLAnchorElement.prototype.click;
            HTMLAnchorElement.prototype.click = function () {
                if (this.download) sessionStorage.setItem("summaryFilename", this.download);
                return originalClick.call(this);
            };
            document.querySelector('input[name="date"]').value = "2026-06-01";
            """)
        self.browser.find_element(
            By.CSS_SELECTOR, '#member-summary-export input[type="submit"]'
        ).click()
        wait.until(EC.presence_of_element_located((By.ID, "result_list")))
        self.assertEqual(self.browser.current_url, url)
        self.assertTrue(
            self.browser.find_element(
                By.CSS_SELECTOR, f'input.action-select[value="{self.member.pk}"]'
            ).is_selected()
        )
        self.assertEqual(
            self.browser.execute_script(
                'return sessionStorage.getItem("summaryFilename")'
            ),
            "medlemsoversigt-2026-06-01.csv",
        )
        self.assertIn(
            self.member.union.name,
            self.browser.execute_script('return sessionStorage.getItem("summaryCsv")'),
        )

    def test_union_export_back_button_restores_selection(self):
        url = self.live_server_url + reverse("admin:members_union_changelist")
        self.browser.get(url)
        selector = f'input.action-select[value="{self.member.union_id}"]'
        self.browser.find_element(By.CSS_SELECTOR, selector).click()
        Select(self.browser.find_element(By.NAME, "action")).select_by_value(
            "export_csv_member_summary"
        )
        self.browser.find_element(By.NAME, "index").click()
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.presence_of_element_located((By.ID, "member-summary-export")))
        self.assertEqual(
            self.browser.find_element(By.ID, "back-to-members").get_attribute("value"),
            "Tilbage til foreningsoversigten",
        )
        self.browser.find_element(By.ID, "back-to-members").click()
        wait.until(EC.presence_of_element_located((By.ID, "result_list")))
        self.assertEqual(self.browser.current_url, url)
        self.assertTrue(
            self.browser.find_element(By.CSS_SELECTOR, selector).is_selected()
        )
