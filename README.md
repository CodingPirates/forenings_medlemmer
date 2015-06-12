install Python 3.4
install pip

pip install -r requirements.txt

./manage.py loaddata fixtures/templates.json

./manage.py migrate

./manage.py runserver

