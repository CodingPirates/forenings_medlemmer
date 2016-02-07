#!/bin/sh

. /opt/virtualenv/forenings_medlemmer/bin/activate

cd /opt/forenings_medlemmer/

export DJANGO_SETTINGS_MODULE=forenings_medlemmer.settings_production

gunicorn --error-logfile /var/log/gunicorn/error.log forenings_medlemmer.wsgi:application

deactivate

