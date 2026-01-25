# Selenium imports

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# NoSuchElementException import removed (unused)
import time
import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from members.models.slackinvitesetup import SlackInvitationSetup
from members.models.slackinvitelog import SlackInviteLog

# send_mail import removed (imported only where needed)

from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


@login_required
def slack_invite_approval(request):
    import time as _time

    if request.method == "POST":
        start_time = _time.time()
        emails_raw = request.POST.get("emails", "")
        purpose = request.POST.get("purpose", "")
        user = request.user
        setup = SlackInvitationSetup.objects.order_by("-updated_at").first()
        invite_url = setup.invite_url if setup else None
        admin_username = setup.admin_username if setup else None
        admin_password = setup.admin_password if setup else None
        # Accept both newlines and spaces as delimiters, but prefer newlines
        emails = []
        for line in emails_raw.splitlines():
            for e in line.strip().split():
                if e:
                    emails.append(e)

        # Defensive: No emails provided
        if not emails:
            messages.error(
                request,
                "Ingen email-adresser blev angivet. Skriv mindst én gyldig email-adresse.",
            )
            return render(
                request,
                "members/slack_invite_approval.html",
                {"emails": emails_raw, "purpose": purpose},
            )

        # Email format validation
        email_regex = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
        invalid_emails = []
        for e in emails:
            # First, use Django validator
            try:
                validate_email(e)
            except ValidationError:
                invalid_emails.append(e)
                continue
            # Then, use stricter regex
            if not email_regex.match(e):
                invalid_emails.append(e)

        if invalid_emails:
            messages.error(
                request, f"Invalid email address(es): {', '.join(invalid_emails)}"
            )
            return render(
                request,
                "members/slack_invite_approval.html",
                {"emails": emails_raw, "purpose": purpose},
            )

        emails_for_slack = " ".join(emails)
        log = SlackInviteLog.objects.create(
            email=emails_for_slack,
            purpose=purpose,
            invite_url=invite_url,
            created_by=user,
            status=1,
        )
        if not invite_url or not admin_username or not admin_password:
            log.status = 3
            log.message = (
                "Slack admin invite URL, username, or password not configured."
            )
            log.save()
            messages.error(
                request, "Slack admin invite URL, username, or password not configured."
            )
            return render(request, "members/slack_invite_approval.html")

        step = "initializing Chrome"
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # Configure binary paths for Docker container
            # Try common locations for Chromium binary
            chromium_paths = [
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/usr/bin/google-chrome",
            ]
            chromium_binary = None
            for path in chromium_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    chromium_binary = path
                    break

            if chromium_binary:
                options.binary_location = chromium_binary
            else:
                error_msg = (
                    f"Chromium binary not found in common locations: {chromium_paths}. "
                    "To troubleshoot in Docker container, run: "
                    "which chromium chromium-browser && ls -la /usr/bin/chromium*"
                )
                raise Exception(error_msg)

            # Try common locations for ChromeDriver
            chromedriver_paths = [
                "/usr/bin/chromedriver",
                "/usr/lib/chromium/chromedriver",
                "/usr/lib/chromium-browser/chromedriver",
            ]
            chromedriver_binary = None
            for path in chromedriver_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    chromedriver_binary = path
                    break

            if chromedriver_binary:
                service = Service(chromedriver_binary)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                error_msg = (
                    f"ChromeDriver not found in common locations: {chromedriver_paths}. "
                    "To troubleshoot in Docker container, run: "
                    "which chromedriver && ls -la /usr/bin/chromedriver /usr/lib/chromium*/chromedriver"
                )
                raise Exception(error_msg)

            step = "loading Slack invite URL"
            driver.get(invite_url)

            # Dismiss cookie banner if present
            try:
                step = "dismissing cookie banner"
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
                ).click()
            except Exception:
                pass  # Banner not present, continue

            step = "waiting for login form"
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "email"))
            )

            step = "entering Slack admin credentials"
            driver.find_element(By.ID, "email").send_keys(admin_username)
            driver.find_element(By.ID, "password").send_keys(admin_password)
            driver.find_element(By.XPATH, '//button[@type="submit"]').click()

            step = "waiting for 'Invite people' button"
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-qa="admin_invite_people_btn"]')
                )
            ).click()

            step = "waiting for invite modal"
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '[data-qa="invite_modal_select-input"]')
                )
            )

            step = "entering emails into invite field"
            invite_input = driver.find_element(
                By.CSS_SELECTOR, '[data-qa="invite_modal_select-input"]'
            )
            from selenium.webdriver.common.keys import Keys

            for email in emails:
                invite_input.send_keys(email)
                invite_input.send_keys(Keys.ENTER)
                time.sleep(0.2)

            step = "dismissing modal overlays before sending"
            try:
                overlays = driver.find_elements(By.CLASS_NAME, "ReactModal__Overlay")
                for overlay in overlays:
                    if overlay.is_displayed():
                        overlay.send_keys(Keys.ESCAPE)
                        time.sleep(0.5)
                        try:
                            close_btn = overlay.find_element(
                                By.XPATH, ".//button[contains(@aria-label, 'Close')]"
                            )
                            close_btn.click()
                            time.sleep(0.5)
                        except Exception:
                            pass
            except Exception:
                pass

            step = "waiting for Send button to be enabled"
            WebDriverWait(driver, 10).until(
                lambda d: d.find_element(
                    By.XPATH,
                    '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]',
                ).is_enabled()
                and not d.find_element(
                    By.XPATH,
                    '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]',
                )
                .get_attribute("class")
                .__contains__("c-button--disabled")
            )

            step = "clicking Send button"
            send_btn = driver.find_element(
                By.XPATH,
                '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]',
            )
            send_btn.click()

            step = "waiting for success indicator"
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[contains(text(), "You\'ve invited")]')
                    )
                )
            except Exception:
                # Try alternate success indicators
                try:
                    driver.find_element(
                        By.XPATH, '//*[contains(text(), "already a member")]'
                    )
                except Exception:
                    try:
                        driver.find_element(
                            By.XPATH, '//*[contains(text(), "already been invited")]'
                        )
                    except Exception:
                        pass

            # If no exception was raised during the process, treat as success
            log.status = 2
            log.save()
            driver.quit()
            processing_time = round(_time.time() - start_time, 2)

        except Exception as e:
            log.status = 3
            page_source = ""
            try:
                page_source = driver.page_source
            except Exception:
                pass
            log.message = f"Selenium error at step: {step}\nException: {e}\n\nPage source:\n{page_source}"
            log.save()
            try:
                driver.quit()
            except Exception:
                pass
            # Send email to setup.emails
            if setup and setup.emails:
                recipients = [
                    em.strip() for em in setup.emails.split(",") if em.strip()
                ]
                from django.core.mail import send_mail

                send_mail(
                    subject="Slack Invite Failure",
                    message=f"Slack invite failed for: {emails_raw}\nPurpose: {purpose}\nStep: {step}\nError: {e}\n\nSee SlackInviteLog for details.",
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=recipients,
                )
            processing_time = round(_time.time() - start_time, 2)
            # Show error to user and preserve form fields
            messages.error(
                request, f"Slack invite failed at step: {step}. Exception: {e}"
            )
            return render(
                request,
                "members/slack_invite_approval.html",
                {
                    "emails": emails_raw,
                    "purpose": purpose,
                },
            )
            driver.quit()
            processing_time = round(_time.time() - start_time, 2)
        # Always show success to user, even if error occurred
        return render(
            request,
            "members/slack_invite_approval.html",
            {
                "success": True,
                "processing_time": processing_time,
                "invited_email": emails_raw,
            },
        )
    return render(request, "members/slack_invite_approval.html")
