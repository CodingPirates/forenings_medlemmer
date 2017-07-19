"""
Django settings for forenings_medlemmer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'el3njbnw)pa)wv0%efsa&214l*5ztei0_)8j3-7#xmxb3ksm-f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

BASE_URL = 'https://members.codingpirates.dk'

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'members',
    'crispy_forms',
    'django_cron',
    'flat_responsive',
    'django.contrib.admin',
    'rest_framework',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'forenings_medlemmer.urls'

WSGI_APPLICATION = 'forenings_medlemmer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'da-dk'

TIME_ZONE = 'Europe/Copenhagen'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_INPUT_FORMATS = (
    '%d-%m-%Y', '%d-%m-%y', # '25-10-06', '25-10-06'
)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

# How many days is Family data considered valid. After this period an E-mail asking for information
# Checkup is sent to the Family.
REQUEST_FAMILY_VALIDATION_PERIOD = 180

STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

ADMINS = (('Administrator', 'admin@example.org'),)
MANAGERS = ADMINS

EMAIL_SUBJECT_PREFIX = '[Acme Medlemsdatabase] '
SERVER_EMAIL = 'hostmaster@example.org'
SITE_CONTACT = 'Acme Industries <contact@example.org>'
DEBUG_EMAIL_DESTINATION = 'debug@example.org'

EMAIL_HOST = 'smtp.example.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'username'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 30

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CRON_CLASSES = [
    "members.jobs.EmailSendCronJob",
    'members.jobs.RequestConfirmationCronJob',
    'members.jobs.SendActivitySignupConfirmationsCronJob',
    'members.jobs.PollQuickpayPaymentsCronJob',
    'members.jobs.GenerateStatisticsCronJob'
]

# Dont keep job logs more than 7 days old
DJANGO_CRON_DELETE_LOGS_OLDER_THAN=7

QUICKPAY_API_KEY='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
QUICKPAY_PRIVATE_KEY='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
