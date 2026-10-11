import logging

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db import transaction
from django.dispatch import receiver

from members.models.authlog import AuthLog

logger = logging.getLogger("members.auth")

Event = AuthLog.Event
SUCCESS_EVENTS = {Event.LOGIN_OK, Event.CODE_OK_NO_AUTOLOGIN}


def client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = forwarded.split(",")[0].strip() if forwarded else None
    return ip or request.META.get("REMOTE_ADDR") or None


def log_auth_event(request, event, identifier="", method="", user=None):
    """Write an authentication event to the log and to the AuthLog table"""
    success = event in SUCCESS_EVENTS
    ip = client_ip(request)
    logger.log(
        logging.INFO if success else logging.WARNING,
        "%s method=%s identifier=%s ip=%s",
        event.label,
        method or "-",
        identifier or "-",
        ip or "-",
    )
    try:
        with transaction.atomic():
            AuthLog.objects.create(
                event=event,
                success=success,
                method=method,
                identifier=(identifier or "")[:254],
                user=user if user is not None and user.pk else None,
                ip_address=ip,
                user_agent=(request.META.get("HTTP_USER_AGENT", "")[:255])
                if request is not None
                else "",
            )
    except Exception:
        logger.exception("Could not save AuthLog entry")


@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    method = getattr(request, "login_method", "password")
    log_auth_event(request, Event.LOGIN_OK, user.get_username(), method, user)


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request=None, **kwargs):
    username = credentials.get("username") or credentials.get("email") or ""
    log_auth_event(request, Event.LOGIN_FAILED, username, "password")
