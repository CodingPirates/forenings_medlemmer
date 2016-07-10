# Coding Pirates medlem og tilmeldings system

## Ved første installation køres:
```
install Python 3.4
install pip

pip install virtualenv
virtualenv -p /usr/bin/python3.4 virtualenv
(måske skal stien til python rettes)

source virtualenv/bin/activate

pip install -r requirements.txt

./manage.py migrate
./manage.py loaddata fixtures/templates.json
./manage.py loaddata fixtures/unions.json
./manage.py loaddata fixtures/departments.json
./manage.py runserver
```

## Herefter kan systemet blot startes med
```
source virtualenv/bin/activate
./manage.py runserver
```

## Efter hver git pull køres:

```
./manage.py migrate
```
