#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd "${DIR}/.." >> /dev/null

gzip --decompress --force --stdout "${DIR}/db_crewmakr.sqlite3.gz" > "${DIR}/../db.sqlite3"

python manage.py migrate
python manage.py loaddata members/fixtures/templates
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell