"""Slack invite approval flow.

Flow summary:
- Log into Slack admin using configured credentials.
- Complete TOTP if configured.
- Open the invite modal.
- Add each email as ``<email> `` so Slack validates token-by-token.
- If Slack marks a token as duplicate/member, click ``Remove duplicate``.
- If Slack marks a token as invalid, click ``Remove all items with errors``.
- After valid emails have been collected, click ``Send`` once.
- Save HTML snapshots and log HTML without embedded ``<script>`` tags.
"""

import os
import random
import re
import time
import tempfile

import pyotp
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from members.models.slackinvitelog import SlackInviteLog
from members.models.slackinvitesetup import SlackInvitationSetup


BROWSER_SELECTION = 1  # 1=Chrome, 2=Firefox
MAX_SNAPSHOT_HTML_CHARS = 250_000
MAX_LOG_HTML_CHARS = 150_000

SCRIPT_TAG_RE = re.compile(
    r"<script\b[^>]*>[\s\S]*?</script\b[^>]*>",
    flags=re.IGNORECASE,
)


def strip_script_tags(html):
    return SCRIPT_TAG_RE.sub("", html or "")


def limit_html_size(html, max_chars):
    html = html or ""
    if len(html) <= max_chars:
        return html
    omitted = len(html) - max_chars
    return html[:max_chars] + f"\n<!-- truncated {omitted} chars -->"


def get_sanitized_page_source(driver, max_chars=None):
    html = ""
    try:
        html = driver.page_source if driver else ""
    except Exception:
        html = ""
    sanitized = strip_script_tags(html)
    if max_chars is not None:
        sanitized = limit_html_size(sanitized, max_chars)
    return sanitized


def save_slack_html(driver, counter, step_name):
    # Only write Slack HTML snapshots when DEBUG is enabled to avoid leaking
    # potentially sensitive admin data and unbounded disk usage in production.
    if not getattr(settings, "DEBUG", False):
        return

    try:
        if not driver:
            return

        # Allow overriding the snapshot directory via settings; otherwise use
        # a subdirectory of the system temporary directory.
        base_dir = getattr(settings, "SLACK_HTML_SNAPSHOT_DIR", None)
        if not base_dir:
            base_dir = os.path.join(tempfile.gettempdir(), "slack-snapshots")

        os.makedirs(base_dir, exist_ok=True)

        safe_step = step_name.replace(" ", "_").replace("'", "").replace('"', "")[:30]
        timestamp_ms = int(time.time() * 1000)
        filename = os.path.join(
            base_dir, f"slack{counter:03d}_{safe_step}_{timestamp_ms}.html"
        )
        with open(filename, "w", encoding="utf-8") as handle:
            handle.write(get_sanitized_page_source(driver, MAX_SNAPSHOT_HTML_CHARS))
    except Exception:
        # Snapshotting should never break the main flow.
        pass


def parse_emails(emails_raw):
    emails = []
    for line in (emails_raw or "").splitlines():
        for email in line.strip().split():
            if email:
                emails.append(email)
    return emails


def normalize_email_text(value):
    return (value or "").strip().lower()


def text_contains_exact_email(text, email):
    normalized_text = normalize_email_text(text)
    normalized_email = normalize_email_text(email)
    if not normalized_text or not normalized_email:
        return False
    pattern = rf"(?<![a-z0-9_.+\-]){re.escape(normalized_email)}(?![a-z0-9_.+\-])"
    return re.search(pattern, normalized_text) is not None


def robust_click(driver, element):
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            element,
        )
    except Exception:
        pass

    try:
        element.click()
        return True
    except Exception:
        pass

    try:
        ActionChains(driver).move_to_element(element).pause(0.1).click().perform()
        return True
    except Exception:
        pass

    try:
        driver.execute_script(
            """
            const el = arguments[0];
            ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(type => {
                el.dispatchEvent(new MouseEvent(type, {
                    bubbles: true,
                    cancelable: true,
                    view: window,
                }));
            });
            """,
            element,
        )
        return True
    except Exception:
        return False


def click_visible_action(driver, labels):
    for label in labels:
        xpaths = [
            f'//button[contains(normalize-space(.), "{label}")]',
            f'//a[contains(normalize-space(.), "{label}")]',
            f'//*[@role="button" and contains(normalize-space(.), "{label}")]',
            f'//span[contains(normalize-space(.), "{label}")]/ancestor::*[self::button or self::a or @role="button"][1]',
        ]
        for xpath in xpaths:
            for element in driver.find_elements(By.XPATH, xpath):
                try:
                    if element.is_displayed() and element.is_enabled():
                        if robust_click(driver, element):
                            return label
                except Exception:
                    continue
    return None


def focus_invite_input(driver):
    input_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '[data-qa="invite_modal_select-input"]')
        )
    )
    try:
        driver.execute_script("arguments[0].focus();", input_element)
    except Exception:
        pass
    return input_element


def clear_invite_query(driver):
    try:
        input_element = focus_invite_input(driver)
        query_text = driver.execute_script(
            """
            const root = arguments[0];
            const query = root.querySelector('.c-multi_select_input__filter_query');
            return query ? query.textContent || '' : '';
            """,
            input_element,
        )
        if query_text:
            for _ in range(len(query_text) + 2):
                input_element.send_keys(Keys.BACKSPACE)
                time.sleep(0.02)
    except Exception:
        pass


def invite_modal_is_open(driver):
    try:
        elements = driver.find_elements(
            By.CSS_SELECTOR, '[data-qa="invite_modal_select-input"]'
        )
        return any(element.is_displayed() for element in elements)
    except Exception:
        return False


def get_invite_tokens(driver):
    tokens = []
    try:
        wrappers = driver.find_elements(
            By.CSS_SELECTOR, '[data-qa="multi_select_token_wrapper"]'
        )
    except Exception:
        return tokens

    for wrapper in wrappers:
        try:
            plain_labels = wrapper.find_elements(
                By.CSS_SELECTOR, '[data-qa="token_plain_label"]'
            )
            error_labels = wrapper.find_elements(
                By.CSS_SELECTOR, '[data-qa="token_error"]'
            )
            label = ""
            is_error = False

            if error_labels:
                label = error_labels[0].text.strip()
                is_error = True
            elif plain_labels:
                label = plain_labels[0].text.strip()

            if not label:
                label = wrapper.text.strip()

            tokens.append(
                {
                    "label": label,
                    "normalized": normalize_email_text(label),
                    "error": is_error
                    or "c-token--error" in (wrapper.get_attribute("class") or ""),
                }
            )
        except Exception:
            continue

    return tokens


def get_token_state(driver, email):
    normalized_email = normalize_email_text(email)
    for token in get_invite_tokens(driver):
        if token["normalized"] == normalized_email:
            return "invalid" if token["error"] else "accepted"
    return None


def remove_token_by_email(driver, email):
    normalized_email = normalize_email_text(email)
    for wrapper in driver.find_elements(
        By.CSS_SELECTOR, '[data-qa="multi_select_token_wrapper"]'
    ):
        try:
            plain_labels = wrapper.find_elements(
                By.CSS_SELECTOR, '[data-qa="token_plain_label"]'
            )
            error_labels = wrapper.find_elements(
                By.CSS_SELECTOR, '[data-qa="token_error"]'
            )
            label = ""
            if error_labels:
                label = error_labels[0].text.strip()
            elif plain_labels:
                label = plain_labels[0].text.strip()
            else:
                label = wrapper.text.strip()

            if normalize_email_text(label) != normalized_email:
                continue

            remove_icon = wrapper.find_element(
                By.CSS_SELECTOR, '[data-qa="token_remove_icon"]'
            )
            if not robust_click(driver, remove_icon):
                continue
            time.sleep(0.2)
            return wait_for_token_removed(driver, email, timeout=2)
        except Exception:
            continue
    return False


def wait_for_token_removed(driver, email, timeout=3):
    normalized_email = normalize_email_text(email)

    def _removed(_driver):
        return get_token_state(_driver, normalized_email) is None

    try:
        WebDriverWait(driver, timeout).until(_removed)
        return True
    except Exception:
        return False


def remove_last_token_with_backspace(driver, email, attempts=3):
    for _ in range(attempts):
        try:
            input_element = focus_invite_input(driver)
            clear_invite_query(driver)
            input_element = focus_invite_input(driver)
            input_element.send_keys(Keys.BACKSPACE)
            time.sleep(0.8)
            if wait_for_token_removed(driver, email, timeout=1.5):
                return True
        except Exception:
            continue
    return False


def remove_invalid_tokens(driver, preferred_email=None):
    removed_labels = []
    initial_error_labels = [
        token["label"] for token in get_invite_tokens(driver) if token["error"]
    ]

    clicked_bulk_action = click_visible_action(driver, ["Remove all items with errors"])
    if clicked_bulk_action:
        time.sleep(1.2)
        for label in initial_error_labels:
            if wait_for_token_removed(driver, label, timeout=2):
                removed_labels.append(label)

    for token in list(get_invite_tokens(driver)):
        if not token["error"]:
            continue
        label = token["label"]
        if remove_token_by_email(driver, label):
            removed_labels.append(label)

    if preferred_email and get_token_state(driver, preferred_email) == "invalid":
        if remove_last_token_with_backspace(driver, preferred_email):
            removed_labels.append(preferred_email)

    clear_invite_query(driver)
    return list(dict.fromkeys(removed_labels))


def email_exists_in_pending_table(driver, email):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-qa="admin_invites_table"]')
            )
        )
        driver.find_element(
            By.XPATH,
            f'//div[@data-qa="invite_email"]//strong[normalize-space(text())="{email}"]',
        )
        return True
    except Exception:
        return False


def wait_for_token_settle(driver, timeout=5):
    def _settled(_driver):
        try:
            input_element = _driver.find_element(
                By.CSS_SELECTOR, '[data-qa="invite_modal_select-input"]'
            )
            query = input_element.find_element(
                By.CSS_SELECTOR, ".c-multi_select_input__filter_query"
            ).text.strip()
            return query == ""
        except Exception:
            return False

    try:
        WebDriverWait(driver, timeout).until(_settled)
        return True
    except Exception:
        return False


def get_visible_validation_texts(driver):
    texts = []
    selectors = [
        (
            By.XPATH,
            '//div[contains(@class, "c-popover__content")]//*[normalize-space(text()) != ""]',
        ),
        (By.XPATH, '//*[@role="alert" and normalize-space(text()) != ""]'),
        (
            By.XPATH,
            '//*[@data-qa="invite_modal_select-options-list"]//*[normalize-space(text()) != ""]',
        ),
    ]
    for selector in selectors:
        try:
            for element in driver.find_elements(*selector):
                text = element.text.strip()
                if text and text not in texts:
                    texts.append(text)
        except Exception:
            continue
    return texts


def classify_validation_state(driver, email):
    matched_texts = [
        text
        for text in get_visible_validation_texts(driver)
        if text_contains_exact_email(text, email)
    ]
    combined_text = " | ".join(matched_texts).lower()
    email_lower = email.lower()
    if email_lower in combined_text:
        duplicate_markers = [
            "already in this workspace",
            "already a member",
            "already been invited",
            "already invited",
            "existing member",
        ]
        invalid_markers = [
            "not a valid email",
            "isn't a valid email",
            "is not a valid email",
            "invalid email",
            "error",
        ]
        if any(marker in combined_text for marker in duplicate_markers):
            return "duplicate", combined_text
        if any(marker in combined_text for marker in invalid_markers):
            return "invalid", combined_text
    return None, combined_text


def build_driver():
    if BROWSER_SELECTION == 1:
        chromedriver_paths = [
            "/usr/bin/chromedriver",
            "/usr/lib/chromium/chromedriver",
            "/usr/lib/chromium-browser/chromedriver",
        ]
        chromedriver_binary = next(
            (
                path
                for path in chromedriver_paths
                if os.path.exists(path) and os.access(path, os.X_OK)
            ),
            None,
        )
        if not chromedriver_binary:
            raise Exception(
                "ChromeDriver not found in common locations: " f"{chromedriver_paths}."
            )
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-sync")
        options.add_argument("--mute-audio")
        options.add_argument(
            "--disable-features=Translate,MediaRouter,OptimizationHints,AutofillServerCommunication"
        )
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_experimental_option(
            "prefs",
            {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_setting_values.geolocation": 2,
                "profile.default_content_setting_values.media_stream": 2,
                "disk-cache-size": 1,
            },
        )
        return webdriver.Chrome(service=Service(chromedriver_binary), options=options)

    if BROWSER_SELECTION == 2:
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService

        geckodriver_paths = ["/usr/bin/geckodriver", "/usr/local/bin/geckodriver"]
        geckodriver_binary = next(
            (
                path
                for path in geckodriver_paths
                if os.path.exists(path) and os.access(path, os.X_OK)
            ),
            None,
        )
        if not geckodriver_binary:
            raise Exception(
                "GeckoDriver not found in common locations: " f"{geckodriver_paths}."
            )
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.page_load_strategy = "eager"
        options.set_preference("permissions.default.image", 2)
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("media.autoplay.default", 5)
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", True)
        options.set_preference("browser.cache.memory.capacity", 16384)
        options.set_preference("browser.sessionhistory.max_total_viewers", 0)
        options.set_preference("toolkit.cosmeticAnimations.enabled", False)
        return webdriver.Firefox(
            service=FirefoxService(geckodriver_binary), options=options
        )

    raise Exception(f"Invalid BROWSER_SELECTION value: {BROWSER_SELECTION}")


@login_required
@permission_required("members.can_approve_slack_invites", raise_exception=True)
def slack_invite_approval(request):
    if request.method != "POST":
        return render(request, "members/slack_invite_approval.html")

    start_time = time.time()
    processing_time = 0
    step = ""
    step_log = []
    driver = None
    html_counter = 1
    success = False
    log = None
    page_source = None
    removed_existing = []
    removed_invalid = []
    invited_emails = []
    result_message = ""
    error_message = None

    emails_raw = request.POST.get("emails", "")
    purpose = request.POST.get("purpose", "")
    emails = parse_emails(emails_raw)

    setup = SlackInvitationSetup.objects.order_by("-updated_at").first()
    invite_url = setup.invite_url if setup else None
    admin_username = setup.admin_username if setup else None
    admin_password = setup.admin_password if setup else None
    totp_secret = setup.totp_secret if setup else None

    log = SlackInviteLog.objects.create(
        status=1,
        purpose=purpose,
        invite_url=invite_url or "",
        created_by=request.user,
        emails="\n".join(emails) if emails else emails_raw,
    )

    def log_step(message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        step_log.append(f"[{timestamp}] {message}")

    def finish(current_success, status=None, extra_html=None):
        nonlocal processing_time
        processing_time = round(time.time() - start_time, 2)
        log.status = status if status is not None else (4 if current_success else 2)
        log.message = "\n".join(step_log)
        if extra_html:
            log.message += "\n\nPage source:\n" + limit_html_size(
                strip_script_tags(extra_html), MAX_LOG_HTML_CHARS
            )
        log.emails = "\n".join(emails) if emails else emails_raw
        log.save()
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        return render(
            request,
            "members/slack_invite_approval.html",
            {
                "success": current_success,
                "processing_time": processing_time,
                "invited_email": emails_raw,
                "emails": emails_raw,
                "purpose": purpose,
                "removed_existing": removed_existing,
                "removed_invalid": removed_invalid,
                "invited_emails": invited_emails,
                "result_message": result_message,
                "error": (
                    None
                    if current_success
                    else (
                        error_message
                        or result_message
                        or "Slack-invitationen blev ikke gennemført."
                    )
                ),
            },
        )

    try:
        if not emails:
            log_step("No emails were provided.")
            error_message = "Der blev ikke angivet nogen email-adresser."
            return finish(False, status=2)

        # Validate and de-duplicate email addresses before starting automation.
        validated_emails = []
        seen_emails = set()
        invalid_emails = []
        for raw_email in emails:
            email = (raw_email or "").strip()
            if not email:
                continue
            if email in seen_emails:
                continue
            try:
                validate_email(email)
            except ValidationError:
                invalid_emails.append(email)
                continue
            seen_emails.add(email)
            validated_emails.append(email)

        if invalid_emails:
            log_step(
                "Invalid email addresses provided: "
                + ", ".join(invalid_emails)
            )
            error_message = (
                "En eller flere email-adresser er ugyldige: "
                + ", ".join(invalid_emails)
            )
            return finish(False, status=2)

        emails = validated_emails

        if not invite_url or not admin_username or not admin_password:
            log_step("Slack invite setup is incomplete.")
            error_message = "Slack invitation setup mangler nødvendige oplysninger."
            return finish(False, status=2)

        driver = build_driver()

        step = "loading Slack invite URL"
        log_step(step)
        driver.get(invite_url)
        save_slack_html(driver, html_counter, step)
        html_counter += 1

        try:
            step = "dismissing cookie banner"
            log_step(step)
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
            ).click()
            save_slack_html(driver, html_counter, step)
            html_counter += 1
        except Exception:
            pass

        step = "waiting for login form"
        log_step(step)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        save_slack_html(driver, html_counter, step)
        html_counter += 1

        step = "entering Slack admin credentials"
        log_step(step)
        driver.find_element(By.ID, "email").send_keys(admin_username)
        time.sleep(random.uniform(1, 2))
        driver.find_element(By.ID, "password").send_keys(admin_password)
        time.sleep(random.uniform(1, 2))
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        save_slack_html(driver, html_counter, step)
        html_counter += 1

        if totp_secret:
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
                    selector_used = selector
                    selector_timings.append(
                        f"Selector {selector} succeeded after {round(time.time() - t0, 2)}s"
                    )
                    break
                except Exception:
                    selector_timings.append(
                        f"Selector {selector} failed after {round(time.time() - t0, 2)}s"
                    )
            for item in selector_timings:
                log_step(f"2FA selector: {item}")
            if not twofa_input:
                log_step("Could not find 2FA input field on Slack login page.")
                return finish(False, status=2)

            log_step(f"2FA input field found with selector: {selector_used}")
            if not twofa_input.is_enabled():
                log_step("2FA input field is disabled.")
                return finish(False, status=2)

            step = "entering TOTP code"
            log_step(step)
            twofa_input.clear()
            twofa_input.send_keys(pyotp.TOTP(totp_secret).now())

            step = "submitting TOTP code"
            log_step(step)
            for btn_selector in [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Verify')]"),
            ]:
                try:
                    button = driver.find_element(*btn_selector)
                    if button.is_enabled():
                        button.click()
                        break
                except Exception:
                    continue
            save_slack_html(driver, html_counter, step)
            html_counter += 1

        step = "waiting for invite people button"
        log_step(step)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-qa="admin_invite_people_btn"]')
            )
        ).click()
        save_slack_html(driver, html_counter, step)
        html_counter += 1

        step = "waiting for invite modal"
        log_step(step)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '[data-qa="invite_modal_select-input"]')
            )
        )
        save_slack_html(driver, html_counter, step)
        html_counter += 1

        accepted_emails = []

        focus_invite_input(driver)

        for email in emails:
            step = f"adding email token: {email}"
            log_step(step)
            if not invite_modal_is_open(driver):
                raise Exception(
                    "Slack invite modal closed unexpectedly during email entry."
                )
            invite_input = focus_invite_input(driver)
            invite_input.send_keys(email)
            invite_input.send_keys(" ")
            time.sleep(0.6)

            if not wait_for_token_settle(driver, timeout=2):
                try:
                    invite_input = focus_invite_input(driver)
                    invite_input.send_keys(Keys.ENTER)
                    time.sleep(0.4)
                except Exception:
                    pass

            if not wait_for_token_settle(driver, timeout=1):
                try:
                    invite_input = focus_invite_input(driver)
                    invite_input.send_keys(Keys.TAB)
                    time.sleep(0.4)
                except Exception:
                    pass

            token_state = get_token_state(driver, email)
            if token_state == "invalid":
                removed_invalid.append(email)
                log_step(
                    f"Slack rendered {email} as an invalid/error token; removing token."
                )
                removed_labels = remove_invalid_tokens(driver, preferred_email=email)
                if removed_labels:
                    log_step(
                        f"Slack removed invalid/error token(s): {', '.join(removed_labels)}"
                    )
                elif get_token_state(driver, email) == "invalid":
                    log_step(
                        f"Slack still shows invalid/error token for {email} after removal attempt."
                    )
                continue
            if token_state == "accepted":
                accepted_emails.append(email)
                log_step(f"Accepted token for {email}.")
                focus_invite_input(driver)
                continue

            action = click_visible_action(
                driver,
                ["Remove duplicate", "Remove all items with errors"],
            )
            if action == "Remove duplicate":
                removed_existing.append(email)
                log_step(f"Slack rejected {email} as duplicate/member; removed token.")
                time.sleep(0.5)
                clear_invite_query(driver)
                continue
            if action == "Remove all items with errors":
                removed_invalid.append(email)
                log_step(f"Slack rejected {email} as invalid; removed token.")
                time.sleep(0.5)
                removed_labels = remove_invalid_tokens(driver, preferred_email=email)
                if removed_labels:
                    log_step(
                        f"Slack removed invalid/error token(s): {', '.join(removed_labels)}"
                    )
                elif get_token_state(driver, email) == "invalid":
                    log_step(
                        f"Slack still shows invalid/error token for {email} after removal attempt."
                    )
                continue

            classification, validation_text = classify_validation_state(driver, email)
            if classification == "duplicate":
                removed_existing.append(email)
                log_step(
                    f"Slack validation marked {email} as existing/already invited: {validation_text}"
                )
                clear_invite_query(driver)
                continue
            if classification == "invalid":
                removed_invalid.append(email)
                log_step(
                    f"Slack validation marked {email} as invalid: {validation_text}"
                )
                removed_labels = remove_invalid_tokens(driver, preferred_email=email)
                if removed_labels:
                    log_step(
                        f"Slack removed invalid/error token(s): {', '.join(removed_labels)}"
                    )
                elif get_token_state(driver, email) == "invalid":
                    log_step(
                        f"Slack still shows invalid/error token for {email} after removal attempt."
                    )
                continue

            wait_for_token_settle(driver, timeout=2)
            token_state = get_token_state(driver, email)
            if token_state == "invalid":
                removed_invalid.append(email)
                log_step(
                    f"Slack left {email} as an invalid/error token after validation; removing token."
                )
                removed_labels = remove_invalid_tokens(driver, preferred_email=email)
                if removed_labels:
                    log_step(
                        f"Slack removed invalid/error token(s): {', '.join(removed_labels)}"
                    )
                elif get_token_state(driver, email) == "invalid":
                    log_step(
                        f"Slack still shows invalid/error token for {email} after removal attempt."
                    )
                continue

            accepted_emails.append(email)
            log_step(f"Accepted token for {email}.")
            focus_invite_input(driver)

        if removed_existing:
            log_step("Duplicate/member emails removed:")
            for email in removed_existing:
                log_step(f"- {email}")
        if removed_invalid:
            log_step("Invalid emails removed:")
            for email in removed_invalid:
                log_step(f"- {email}")

        if not accepted_emails:
            log_step("No valid emails remained after Slack validation.")
            result_message = "Ingen adresser kunne inviteres. Alle adresser blev enten genkendt som eksisterende eller afvist som ugyldige."
            return finish(True, status=4)

        step = "clicking Send button"
        log_step(step)
        send_btn = driver.find_element(
            By.XPATH,
            '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]',
        )
        send_btn_class = send_btn.get_attribute("class") or ""
        send_btn_aria_disabled = send_btn.get_attribute("aria-disabled")
        log_step(
            f"Send button state: class='{send_btn_class}', aria-disabled='{send_btn_aria_disabled}'"
        )
        if "c-button--disabled" in send_btn_class or send_btn_aria_disabled == "true":
            log_step("Send button remained disabled after validation.")
            token_snapshot = [
                f"{token['label']} ({'error' if token['error'] else 'ok'})"
                for token in get_invite_tokens(driver)
            ]
            if token_snapshot:
                log_step("Token snapshot before retry: " + ", ".join(token_snapshot))
            leftover_error_tokens = [
                token["label"] for token in get_invite_tokens(driver) if token["error"]
            ]
            if leftover_error_tokens:
                for token_label in leftover_error_tokens:
                    if token_label not in removed_invalid:
                        removed_invalid.append(token_label)
                    if token_label in accepted_emails:
                        accepted_emails.remove(token_label)
                    log_step(
                        f"Removing leftover invalid/error token before retrying Send: {token_label}"
                    )

                removed_labels = remove_invalid_tokens(
                    driver, preferred_email=leftover_error_tokens[0]
                )
                if removed_labels:
                    log_step(
                        f"Slack removed leftover invalid/error token(s): {', '.join(removed_labels)}"
                    )

            if leftover_error_tokens:
                time.sleep(0.5)
                token_snapshot = [
                    f"{token['label']} ({'error' if token['error'] else 'ok'})"
                    for token in get_invite_tokens(driver)
                ]
                if token_snapshot:
                    log_step(
                        "Token snapshot after retry cleanup: "
                        + ", ".join(token_snapshot)
                    )
                send_btn = driver.find_element(
                    By.XPATH,
                    '//button[@aria-label="Send" and @type="button" and contains(@class, "c-button--primary")]',
                )
                send_btn_class = send_btn.get_attribute("class") or ""
                send_btn_aria_disabled = send_btn.get_attribute("aria-disabled")
                log_step(
                    "Send button state after removing leftover error tokens: "
                    f"class='{send_btn_class}', aria-disabled='{send_btn_aria_disabled}'"
                )

            for email in list(accepted_emails):
                classification, validation_text = classify_validation_state(
                    driver, email
                )
                if classification == "duplicate" and email not in removed_existing:
                    removed_existing.append(email)
                    accepted_emails.remove(email)
                    log_step(
                        f"Reclassified {email} as existing/already invited: {validation_text}"
                    )
                elif classification == "invalid" and email not in removed_invalid:
                    removed_invalid.append(email)
                    accepted_emails.remove(email)
                    log_step(f"Reclassified {email} as invalid: {validation_text}")
            if not accepted_emails:
                result_message = "Ingen adresser kunne inviteres. Alle adresser blev enten genkendt som eksisterende eller afvist som ugyldige."
                return finish(True, status=4)
            if (
                "c-button--disabled" not in send_btn_class
                and send_btn_aria_disabled != "true"
            ):
                send_btn.click()
                time.sleep(random.uniform(2.5, 4.0))
                save_slack_html(driver, html_counter, step)
                html_counter += 1
            else:
                page_source = get_sanitized_page_source(driver, MAX_LOG_HTML_CHARS)
                error_message = "Slack holdt Send-knappen deaktiveret efter validering."
                result_message = "Slack holdt Send-knappen deaktiveret, selv om nogle adresser så gyldige ud."
                return finish(False, status=2, extra_html=page_source)
        else:
            send_btn.click()
            time.sleep(random.uniform(2.5, 4.0))
            save_slack_html(driver, html_counter, step)
            html_counter += 1

        step = "reading confirmation modal"
        log_step(step)
        confirmation_text = ""
        try:
            modal = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//div[contains(@class, "c-sk-modal")]')
                )
            )
            confirmation_text = modal.text.strip()
            if confirmation_text:
                log_step(f"Invite modal text after Send: {confirmation_text}")
        except Exception:
            log_step("Could not read confirmation modal after clicking Send.")

        confirmed_emails = [
            email for email in accepted_emails if email in confirmation_text
        ]
        if confirmed_emails:
            invited_emails[:] = confirmed_emails
            log_step("Confirmed invited emails:")
            for email in confirmed_emails:
                log_step(f"- {email}")
        elif accepted_emails and "Sent" in confirmation_text:
            invited_emails[:] = accepted_emails

        finish_button = click_visible_action(driver, ["Finished", "Done", "Close"])
        if finish_button:
            log_step(f"Closed confirmation modal using '{finish_button}'.")

        invited_from_table = []
        for email in accepted_emails:
            if email_exists_in_pending_table(driver, email):
                invited_from_table.append(email)

        if invited_from_table:
            invited_emails[:] = invited_from_table
            log_step("Verified invited emails from pending invites table:")
            for email in invited_from_table:
                log_step(f"- {email}")

        success = bool(confirmed_emails) or (
            "Sent" in confirmation_text and bool(accepted_emails)
        )
        if invited_from_table:
            success = True
        if invited_emails:
            result_message = f"{len(invited_emails)} adresse(r) blev inviteret."
        elif removed_existing or removed_invalid:
            result_message = (
                "Slack behandlede adresserne, men ingen nye invitationer blev sendt."
            )
        if not success:
            page_source = get_sanitized_page_source(driver, MAX_LOG_HTML_CHARS)
            error_message = "Slack gennemførte ikke invitationen fuldt ud."

        return finish(
            success,
            status=4 if success else 2,
            extra_html=None if success else page_source,
        )

    except Exception as exc:
        log_step(f"ERROR: {exc}")
        error_message = (
            "Der opstod en uventet fejl under Slack-invitationen. "
            "Administratoren er blevet informeret."
        )
        try:
            page_source = get_sanitized_page_source(driver, MAX_LOG_HTML_CHARS)
        except Exception:
            page_source = ""

        if setup and setup.emails:
            recipients = [
                email.strip() for email in setup.emails.splitlines() if email.strip()
            ]
            if recipients:
                send_mail(
                    subject="Slack Invite Failure",
                    message=(
                        f"Slack invite failed for: {emails_raw}\n"
                        f"Purpose: {purpose}\n"
                        f"Step: {step}\n"
                        f"Error: {exc}\n\n"
                        "See SlackInviteLog for details."
                    ),
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=recipients,
                )

        return finish(False, status=2, extra_html=page_source)
