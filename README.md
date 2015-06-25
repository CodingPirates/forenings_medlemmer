Ved første installation køres:
install Python 3.4
install pip

pip install virtualenv
virtualenv -p /usr/bin/python3.4 venv
(måske skal stien til python rettes)

source venv/bin/activate

pip install -r requirements.txt

./manage.py loaddata fixtures/templates.json
./manage.py migrate
./manage.py runserver

Herefter kan systemet blot startes med
source venv/bin/activate
./manage.py runserver


Efter hver git pull køres:
./manage.py migrate

