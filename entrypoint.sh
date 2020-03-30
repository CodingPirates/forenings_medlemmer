#!/bin/sh
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Compile sass
/bin/dart-sass/sass \
    members/static/members/sass/main.scss members/static/members/css/main.css

python manage.py migrate
python manage.py dump_public_data
python manage.py collectstatic --no-input --clear
exec "$@"
