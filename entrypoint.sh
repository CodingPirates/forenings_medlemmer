#!/bin/sh
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Compile less
lessc members/static/members/less/main.less members/static/members/css/compiled_less.css

python manage.py migrate
python manage.py collectstatic --no-input --clear
exec "$@"
