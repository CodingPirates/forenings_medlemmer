#!/bin/sh

. /opt/virtualenv/forenings_medlemmer/bin/activate

cd /opt/forenings_medlemmer/

export DJANGO_SETTINGS_MODULE=forenings_medlemmer.settings_production

./manage.py runcrons

deactivate

