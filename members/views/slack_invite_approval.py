import time
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from members.models.slackinvitesetup import SlackInvitationSetup
from members.models.slackinvitelog import SlackInviteLog

from django.core.mail import send_mail
from django.conf import settings

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


@login_required
@csrf_protect
def slack_invite_approval(request):
    if request.method == "POST":
        email = request.POST.get("email")
        full_name = request.POST.get("full_name")
        purpose = request.POST.get("purpose")
        user = request.user
        # Get the latest Slack invite URL from setup
        setup = SlackInvitationSetup.objects.order_by("-updated_at").first()
        invite_url = setup.invite_url if setup else None
        log = SlackInviteLog.objects.create(
            name=full_name,
            email=email,
            purpose=purpose,
            invite_url=invite_url,
            created_by=user,
            status=1,
        )
        if not invite_url:
            log.status = 3
            log.message = "No Slack invite URL configured."
            log.save()
            # Send email to admins
            if setup and setup.emails:
                recipients = [e.strip() for e in setup.emails.split(",") if e.strip()]
                send_mail(
                    subject="Slack Invite Failure",
                    message=f"Slack invite failed for {email} ({full_name}). Reason: No Slack invite URL configured.",
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=recipients,
                )
            messages.error(request, "No Slack invite URL configured.")
            return render(request, "members/slack_invite_approval.html")
        # --- Selenium logic ---
        try:
            driver = webdriver.Chrome()  # Or use Firefox, etc.
            driver.get(invite_url)
            time.sleep(2)
            # Click "Continue With Email"
            try:
                continue_btn = driver.find_element(
                    By.XPATH, '//span[contains(text(), "Continue With Email")]/..'
                )
                continue_btn.click()
            except NoSuchElementException:
                log.status = 3
                log.message = driver.page_source
                log.save()
                driver.quit()
                # Send email to admins
                if setup and setup.emails:
                    recipients = [
                        e.strip() for e in setup.emails.split(",") if e.strip()
                    ]
                    send_mail(
                        subject="Slack Invite Failure",
                        message=f"Slack invite failed for {email} ({full_name}). Could not find 'Continue With Email' button.\n\nHTML:\n{log.message}",
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                        recipient_list=recipients,
                    )
                messages.error(request, "Could not find 'Continue With Email' button.")
                return render(request, "members/slack_invite_approval.html")
            time.sleep(1)
            # Fill email
            email_input = driver.find_element(By.ID, "email")
            email_input.clear()
            email_input.send_keys(email)
            # Fill full name
            name_input = driver.find_element(By.ID, "real_name")
            name_input.clear()
            name_input.send_keys(full_name)
            # Click submit
            submit_btn = driver.find_element(
                By.XPATH,
                '//button[@type="submit" and contains(text(), "Continue With Email")]',
            )
            submit_btn.click()
            log.status = 2
            log.save()
            driver.quit()
            messages.success(request, "Slack invite submitted successfully.")
        except Exception as e:
            log.status = 3
            log.message = str(e)
            log.save()
            # Send email to admins
            if setup and setup.emails:
                recipients = [e.strip() for e in setup.emails.split(",") if e.strip()]
                send_mail(
                    subject="Slack Invite Failure",
                    message=f"Slack invite failed for {email} ({full_name}). Error: {e}",
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=recipients,
                )
            messages.error(request, f"Slack invite failed: {e}")
        return render(request, "members/slack_invite_approval.html")
    return render(request, "members/slack_invite_approval.html")
