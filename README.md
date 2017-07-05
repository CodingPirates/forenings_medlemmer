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
./manage.py loaddata members/fixtures/templates.json
./manage.py loaddata members/fixtures/unions.json
./manage.py loaddata members/fixtures/departments.json
./manage.py createsuperuser
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

## Email og andre cron jobs

Email bliver sendt via et cron job, så for at modtage email skal du køre følgende kommando:

```
./manage.py runcrons
```

Andre opgaver der foretages af cron jobs er defineret som funktioner i members/jobs.py
