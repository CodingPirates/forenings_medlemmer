from cookie_consent.models import Cookie, CookieGroup
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


class CookieDeclarationPageTestCase(TestCase):
    def setUp(self):
        self.group = CookieGroup.objects.create(
            varname="necessary",
            name="Nødvendige cookies",
            description="Disse cookies er nødvendige for at Medlemssystemet kan fungere.",
            is_required=True,
            is_deletable=False,
        )
        Cookie.objects.create(
            cookiegroup=self.group,
            name="sessionid",
            domain="",
            description="Bruges til at holde dig logget ind.",
        )

    def test_cookie_group_list_page_shows_declared_cookies_in_danish(self):
        response = self.client.get(reverse("cookie_consent_cookie_group_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nødvendige cookies")
        self.assertContains(response, "sessionid")
        self.assertContains(response, "Bruges til at holde dig logget ind.")

    def test_required_group_has_no_accept_or_decline_buttons(self):
        # Required cookies can't be declined, so there's nothing to choose here.
        response = self.client.get(reverse("cookie_consent_cookie_group_list"))

        self.assertNotContains(response, "cookie-consent-accept")
        self.assertNotContains(response, "cookie-consent-decline")

    def test_footer_links_to_cookie_declaration_page(self):
        response = self.client.get(reverse("person_login"))

        self.assertContains(
            response, f'href="{reverse("cookie_consent_cookie_group_list")}"'
        )


class SeedCookieConsentCommandTestCase(TestCase):
    def test_command_creates_necessary_group_with_descriptions(self):
        call_command("seed_cookie_consent")

        group = CookieGroup.objects.get(varname="necessary")
        self.assertTrue(group.is_required)
        self.assertFalse(group.is_deletable)

        cookies = {cookie.name: cookie.description for cookie in group.cookie_set.all()}
        self.assertIn("sessionid", cookies)
        self.assertIn("csrftoken", cookies)
        self.assertTrue(all(cookies.values()))

    def test_command_is_idempotent_and_backfills_descriptions(self):
        group = CookieGroup.objects.create(varname="necessary", name="Nødvendige cookies")
        Cookie.objects.create(cookiegroup=group, name="sessionid", domain="")

        call_command("seed_cookie_consent")
        call_command("seed_cookie_consent")

        self.assertEqual(CookieGroup.objects.filter(varname="necessary").count(), 1)
        cookie = Cookie.objects.get(cookiegroup=group, name="sessionid")
        self.assertTrue(cookie.description)
