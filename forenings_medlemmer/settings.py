"""
Django settings for forenings_medlemmer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import logging
from environs import Env
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


env = Env()
env.read_env()

if env.str("SENTRY_DSN") != "not set":
    sentry_sdk.init(
        dsn=env.str("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        environment=env.str("MODE"),
    )

logger = logging.getLogger(__name__)

TESTING = os.path.basename(sys.argv[1]) == "test"
USE_DAWA_ON_SAVE = not TESTING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # insert your TEMPLATE_DIRS here
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG")
if DEBUG:
    logger.warning("RUNNING IN DEBUG MODE")
else:
    logger.info("RUNNING IN PRODUCTION")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ALLOWED_HOSTS = [host.replace(" ", "") for host in env.list("ALLOWED_HOSTS")]
BASE_URL = os.environ["BASE_URL"]
assert not BASE_URL.endswith(
    "/"
), f"BASE_URL environment variable must not end with '/'. It is set to '{BASE_URL}'."

INSTALLED_APPS = (
    "django_bootstrap5",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "members",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_cron",
    "django.contrib.admin",
    "graphene_django",
    "django_extensions",
)

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.environ["DATA_UPLOAD_MAX_NUMBER_FIELDS"])

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
)

CORS_ORIGIN_WHITELIST = [host.replace(" ", "") for host in env.list("CORS_LIST")]
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = "forenings_medlemmer.urls"
CORS_ORIGIN_ALLOW_ALL = True

WSGI_APPLICATION = "forenings_medlemmer.wsgi.application"

GRAPHENE = {"SCHEMA": "members.schema.schema"}

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
# DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"])}

if env.bool("USE_SQLITE", False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "members.db",
        }
    }
else:
    DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"])}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = "da-dk"

TIME_ZONE = "Europe/Copenhagen"

USE_I18N = True

USE_TZ = True

DATE_INPUT_FORMATS = ("%d/%m/%Y", "%Y-%m-%d")

# How many days is Family data considered valid.
# After this period an E-mail asking for information
# Checkup is sent to the Family.
REQUEST_FAMILY_VALIDATION_PERIOD = 180

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
ADMIN_MEDIA_PREFIX = "/static/admin/"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets")]
ADMINS = eval(os.environ["ADMINS"])
MANAGERS = ADMINS


SITE_CONTACT = "Coding Pirates <kontakt@codingpirates.dk>"
EMAIL_SUBJECT_PREFIX = "[Coding Pirates Medlemsdatabase] "
email = env.dj_email_url("EMAIL_URL")
EMAIL_BACKEND = email["EMAIL_BACKEND"]
EMAIL_HOST = email["EMAIL_HOST"]
EMAIL_HOST_USER = email["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = email["EMAIL_HOST_PASSWORD"]
EMAIL_FILE_PATH = BASE_DIR
SERVER_EMAIL = "hostmaster@members.codingpirates.dk"
EMAIL_PORT = email["EMAIL_PORT"]
EMAIL_USE_SSL = email["EMAIL_USE_SSL"]
DEFAULT_FROM_EMAIL = "kontakt@codingpirates.dk"
EMAIL_TIMEOUT = 30

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

AUTHENTICATION_BACKENDS = ("members.backends.CaseInsensitiveModelBackend",)


CRON_CLASSES = [
    "members.jobs.EmailSendCronJob",
    # job disabled due to upcomming change to login, which will
    # require everyone to access the site anyway
    #   'members.jobs.RequestConfirmationCronJob',
    "members.jobs.SendActivitySignupConfirmationsCronJob",
    "members.jobs.PollQuickpayPaymentsCronJob",
    "members.jobs.UpdateDawaData",
    "members.jobs.CaptureOutstandingPayments",
]

# Dont keep job logs more than 7 days old
DJANGO_CRON_DELETE_LOGS_OLDER_THAN = 7

QUICKPAY_API_KEY = os.environ["QUICKPAY_API_KEY"]
QUICKPAY_PRIVATE_KEY = os.environ["QUICKPAY_PRIVATE_KEY"]
PAYMENT_ID_PREFIX = env.str("PAYMENT_ID_PREFIX")
if (
    PAYMENT_ID_PREFIX != "prod"
    and len(PAYMENT_ID_PREFIX) < 1
    or len(PAYMENT_ID_PREFIX) > 3
):
    raise EnvironmentError("PAYMENT_ID_PREFIX must be between 1 and 3 chars")


SECURE_SSL_REDIRECT = env.bool("FORCE_HTTPS")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True


LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URL = "/"
