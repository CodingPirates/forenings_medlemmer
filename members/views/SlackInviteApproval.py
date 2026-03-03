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
import pyotp
import random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re



@login_required
def slack_invite_approval(request):
    # Helper to save page source to incrementing files
    def save_slack_html(counter, step_name):
        log = None
        try:
            if not os.path.exists("test-screens"):
                os.mkdir("test-screens")
            safe_step = step_name.replace(" ", "_").replace("'", "").replace('"', "")[:30]
            filename = os.path.join("test-screens", f"slack{counter}_{safe_step}.html")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except Exception:
            pass
    import time as _time

    if request.method == "POST":
        start_time = _time.time()
        step_log = []
        step = ""
        driver = None
        log = SlackInviteLog()
        options = None
        html_counter = 1
        def log_step(step_name):
            t = time.strftime("%Y-%m-%d %H:%M:%S")
            step_log.append(f"[{t}] {step_name}")

        log_step("POST request received - start Slack invite flow")
        emails_raw = request.POST.get("emails", "")
        purpose = request.POST.get("purpose", "")
        user = request.user
        setup = SlackInvitationSetup.objects.order_by("-updated_at").first()
        invite_url = setup.invite_url if setup else None
        admin_username = setup.admin_username if setup else None
        admin_password = setup.admin_password if setup else None
        totp_secret = setup.totp_secret if setup else None
        # Accept both newlines and spaces as delimiters, but prefer newlines
        emails = []
        for line in emails_raw.splitlines():
            for e in line.strip().split():
                if e:
                    emails.append(e)

        # Defensive: No emails provided
        try:
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
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                driver = webdriver.Chrome(service=service, options=options)
            else:
                error_msg = (
                    f"ChromeDriver not found in common locations: {chromedriver_paths}. "
                    "To troubleshoot in Docker container, run: "
                    "which chromedriver && ls -la /usr/bin/chromedriver /usr/lib/chromium*/chromedriver"
                )
                raise Exception(error_msg)

            step = "loading Slack invite URL"
            log_step(step)
            driver.get(invite_url)

            save_slack_html(html_counter, step)
            html_counter += 1

            # Dismiss cookie banner if present
            try:
                step = "dismissing cookie banner"
                log_step(step)
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
                ).click()
                save_slack_html(html_counter, step)
                html_counter += 1
            except Exception:
                pass  # Banner not present, continue

            step = "waiting for login form"
            log_step(step)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "email"))
            )

            save_slack_html(html_counter, step)
            html_counter += 1

            step = "entering Slack admin credentials"
            log_step(step)
            time.sleep(random.uniform(1, 2))
            driver.find_element(By.ID, "email").send_keys(admin_username)
            time.sleep(random.uniform(2, 3))
            driver.find_element(By.ID, "password").send_keys(admin_password)
            # Tilføj menneskelig pause før login
            time.sleep(random.uniform(1, 2))
            driver.find_element(By.XPATH, '//button[@type="submit"]').click()

            save_slack_html(html_counter, step)
            html_counter += 1

            # --- 2FA TOTP step ---
            if totp_secret:
                try:
                    # Vent på at 2FA-feltet vises (kan hedde '2fa_code', 'totp', eller lignende)
                    step = "waiting for 2FA input field"
                    log_step(step)
                    twofa_input = None
                    selector_used = None
                    selector_timings = []
                    for selector in [
                        (By.CSS_SELECTOR, "input[type='text']"),
                        (By.ID, "2fa_code"),
                        (By.ID, "totp"),
                        (By.NAME, "2fa_code"),
                        (By.NAME, "totp"),
                        (By.CSS_SELECTOR, "input[type='tel']"),
                    ]:
                        t0 = time.time()
                        try:
                            twofa_input = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(selector)
                            )
                            dt = round(time.time() - t0, 2)
                            selector_timings.append(
                                f"Selector {selector} succeeded after {dt}s"
                            )
                            selector_used = selector
                            break
                        except Exception:
                            dt = round(time.time() - t0, 2)
                            selector_timings.append(
                                f"Selector {selector} failed after {dt}s"
                            )
                            continue
                    for sel_log in selector_timings:
                        log_step(f"2FA selector: {sel_log}")
                    if not twofa_input:
                        raise Exception(
                            "Could not find 2FA input field on Slack login page."
                        )
                    log_step(f"2FA input field found with selector: {selector_used}")
                    # Menneskelig pause før TOTP-kode genereres og indtastes
                    time.sleep(random.uniform(2, 5))
                    totp_code = pyotp.TOTP(totp_secret).now()
                    twofa_input.clear()
                    step = "entering TOTP code"
                    log_step(step)
                    twofa_input.send_keys(totp_code)
                    # Find og klik på knappen for at fortsætte (kan være 'submit', 'Verify', etc.)
                    step = "submitting TOTP code"
                    log_step(step)
                    for btn_selector in [
                        (By.XPATH, "//button[@type='submit']"),
                        (By.XPATH, "//button[contains(text(), 'Verify')]"),
                    ]:
                        try:
                            btn = driver.find_element(*btn_selector)
                            if btn.is_enabled():
                                btn.click()
                                break
                        except Exception:
                            continue
                    save_slack_html(html_counter, step)
                    html_counter += 1
                except Exception as e:
                    step = f"2FA step failed: {e}"
                    raise

            step = "waiting for 'Invite people' button"
            log_step(step)
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-qa="admin_invite_people_btn"]')
                )
            ).click()

            save_slack_html(html_counter, step)
            html_counter += 1

            step = "waiting for invite modal"
            log_step(step)
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '[data-qa="invite_modal_select-input"]')
                )
            )

            save_slack_html(html_counter, step)
            html_counter += 1

            step = "entering emails into invite field"
            log_step(step)
            invite_input = driver.find_element(
                By.CSS_SELECTOR, '[data-qa="invite_modal_select-input"]'
            )
            from selenium.webdriver.common.keys import Keys


            for email in emails:
                for char in email:
                    invite_input.send_keys(char)
                    time.sleep(random.uniform(0.2, 0.25))
                invite_input.send_keys(Keys.SPACE)
                time.sleep(0.2)

                # Wait for Slack's online validation to complete (Send button enabled)
                try:
                    WebDriverWait(driver, 10).until(
                        lambda d: d.find_element(
                            By.XPATH,
                            '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]'
                        ).is_enabled()
                        and not d.find_element(
                            By.XPATH,
                            '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]'
                        ).get_attribute("class").__contains__("c-button--disabled")
                    )
                    log_step(f"Email '{email}' validated and Send button enabled.")
                except Exception:
                    log_step(f"Email '{email}' did not pass validation or Send button not enabled in time.")

            # Now use Tab navigation to reach Send button and press Enter
            invite_input.click()
            time.sleep(0.5)
            send_btn = None
            for _ in range(10):
                invite_input.send_keys(Keys.TAB)
                time.sleep(0.2)
                active = driver.switch_to.active_element
                if (
                    active.tag_name == "button"
                    and active.get_attribute("aria-label") == "Send"
                    and "c-button--primary" in active.get_attribute("class")
                ):
                    send_btn = active
                    break
            if send_btn:
                send_btn.send_keys(Keys.ENTER)
                log_step("Activated Send button using keyboard navigation (Tab + Enter)")
            else:
                log_step("Could not focus Send button using Tab navigation; falling back to click.")
                send_btn = driver.find_element(
                    By.XPATH,
                    '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]'
                )
                send_btn.click()
            time.sleep(random.uniform(2.5, 4.5))

            # --- Enhanced diagnostics after clicking Send ---
            try:
                aria_msgs = []
                for sel in [
                    (By.XPATH, '//*[@role="alert" and string-length(normalize-space(text())) > 0]'),
                    (By.XPATH, '//*[@aria-live="assertive" and string-length(normalize-space(text())) > 0]'),
                    (By.XPATH, '//*[@aria-live="polite" and string-length(normalize-space(text())) > 0]'),
                ]:
                    for el in driver.find_elements(*sel):
                        txt = el.text.strip()
                        if txt:
                            aria_msgs.append(txt)
                if aria_msgs:
                    log_step(f"ARIA live region(s) after Send: {' | '.join(aria_msgs)}")
            except Exception:
                pass

            try:
                modal = driver.find_element(By.XPATH, '//div[contains(@class, "c-sk-modal")]')
                modal_text = modal.text.strip()
                if modal_text:
                    log_step(f"Invite modal text after Send: {modal_text}")
            except Exception:
                log_step("Could not extract invite modal text after Send click.")

            save_slack_html(html_counter, step)
            html_counter += 1
            send_btn = driver.find_element(
                By.XPATH,
                '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]',
            )

            send_btn = driver.find_element(
                By.XPATH,
                '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]',
            )

            send_btn.click()
            # Add a longer random delay to mimic human behavior and allow UI updates
            time.sleep(random.uniform(2.5, 4.5))

            # --- Enhanced diagnostics after clicking Send ---
            # 1. Log ARIA live region contents (role="alert", aria-live="assertive"/"polite")
            try:
                aria_msgs = []
                for sel in [
                    (By.XPATH, '//*[@role="alert" and string-length(normalize-space(text())) > 0]'),
                    (By.XPATH, '//*[@aria-live="assertive" and string-length(normalize-space(text())) > 0]'),
                    (By.XPATH, '//*[@aria-live="polite" and string-length(normalize-space(text())) > 0]'),
                ]:
                    for el in driver.find_elements(*sel):
                        txt = el.text.strip()
                        if txt:
                            aria_msgs.append(txt)
                if aria_msgs:
                    log_step(f"ARIA live region(s) after Send: {' | '.join(aria_msgs)}")
            except Exception:
                pass

            # 2. Log all visible modal text after clicking Send
            try:
                modal = driver.find_element(By.XPATH, '//div[contains(@class, "c-sk-modal")]')
                modal_text = modal.text.strip()
                if modal_text:
                    log_step(f"Invite modal text after Send: {modal_text}")
            except Exception:
                log_step("Could not extract invite modal text after Send click.")

            save_slack_html(html_counter, step)
            html_counter += 1


            step = "waiting for success indicator or pending invite row"
            log_step(step)
            save_slack_html(html_counter, step)
            html_counter += 1
            success = False
            page_source = None
            invited_email = emails[0] if emails else None

            # --- NEW: Check for error/validation messages in the invite modal ---
            error_text = None
            try:
                # Look for common error/validation message containers in the invite modal
                # Slack often uses elements with role="alert" or aria-live="assertive" for errors
                error_elements = driver.find_elements(By.XPATH, '//*[(@role="alert" or @aria-live="assertive") and string-length(normalize-space(text())) > 0]')
                if error_elements:
                    error_texts = [el.text.strip() for el in error_elements if el.text.strip()]
                    if error_texts:
                        error_text = " | ".join(error_texts)
                        log_step(f"Invite modal error detected: {error_text}")
                        success = False
                        page_source = driver.page_source
            except Exception:
                pass

            if error_text:
                # If error detected, log and skip further success checks
                log_step(f"Invite failed due to modal error: {error_text}")
            else:
                try:
                    # First, try the classic success indicators
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[contains(text(), "You\'ve invited")]')
                        )
                    )
                    success = True
                except Exception:
                    # Try alternate success indicators
                    try:
                        driver.find_element(
                            By.XPATH, '//*[contains(text(), "already a member")]'
                        )
                        success = True
                    except Exception:
                        try:
                            driver.find_element(
                                By.XPATH, '//*[contains(text(), "already been invited")]'
                            )
                            success = True
                        except Exception:
                            pass
                    # If still not successful, check for the invited email in the pending invites table
                    if not success and invited_email:
                        try:
                            # Wait for the pending invites table to appear
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-qa="admin_invites_table"]'))
                            )
                            # Look for the invited email in the table
                            email_xpath = f'//div[@data-qa="invite_email"]//strong[contains(text(), "{invited_email}")]'
                            driver.find_element(By.XPATH, email_xpath)
                            success = True
                            log_step(f"Found invited email '{invited_email}' in pending invites table")
                        except Exception:
                            pass
                    # If still not successful, capture the page source for debugging
                    if not success:
                        try:
                            page_source = driver.page_source
                        except Exception:
                            page_source = None

            if success:
                log_step("flow complete - all steps done")
                log.status = 4  # Success
                log.message = "\n".join(step_log)
            else:
                log_step("invite likely failed - no success indicator found")
                log.status = 2  # Failed
                log.message = "\n".join(step_log)
                if page_source:
                    log.message += "\n\nPage source after clicking Send:\n" + page_source
            log.save()
            driver.quit()
            processing_time = round(_time.time() - start_time, 2)

        except Exception as e:
            log_step(f"ERROR: {e}")
            page_source = ""
            if driver:
                try:
                    page_source = driver.page_source
                except Exception:
                    pass
            if log is not None:
                log.status = 3
                log.message = f"{''.join(step_log)}\n\nSelenium error at step: {step}\nException: {e}\n\nPage source:\n{page_source}"
                log.save()
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            # Send email to setup.emails
            if setup and setup.emails:
                recipients = [
                    em.strip() for em in setup.emails.splitlines() if em.strip()
                ]
                from django.core.mail import send_mail

                send_mail(
                    subject="Slack Invite Failure",
                    message=f"Slack invite failed for: {emails_raw}\nPurpose: {purpose}\nStep: {step}\nError: {e}\n\nSee SlackInviteLog for details.",
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=recipients,
                )
            processing_time = round(_time.time() - start_time, 2)
            # Vis altid succes til bruger, selv ved fejl
            return render(
                request,
                "members/slack_invite_approval.html",
                {
                    "success": True,
                    "processing_time": processing_time,
                    "invited_email": emails_raw,
                },
            )
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
