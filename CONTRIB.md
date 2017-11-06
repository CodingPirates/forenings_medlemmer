Før du går i gang med at kode så stik endelig forbi [slack](https://codingpirates.signup.team) 
og fortæl os om det du vil udvikle på, det kan jo tænkes vi allerede er i gang med det. 


## Første gangs opsætning
For at kunne køre medlemssystemet skal du have installeret python 3.4 eller senere og pip

De følgende kommandoer vil få dig hurtigt i gang og op at køre:
```
# git clone git@github.com:CodingPirates/forenings_medlemmer.git
# cd forenings_medlemmer
# pip install virtualenv

For Linux-brugere: {
	# virtualenv -p $(/usr/bin/env python3) virtualenv
	# source virtualenv/bin/activate
}

For Windows-brugere: {
	# virtualenv virtualenv
	# virtualenv/Scripts/activate
}

# pip install -r requirements.txt
# ./manage.py migrate
# ./manage.py loaddata fixtures/templates.json
# ./manage.py loaddata fixtures/unions.json
# ./manage.py loaddata fixtures/departments.json
# ./manage.py createsuperuser
# ./manage.py runserver
```

Systemet er nu kørende og du kan tilgå admin interfacet gennem 
[localhost:8000/admin](http://localhost:8000/admin)

Hver gang du vil arbejde på systemet køres 
```
# source virtualenv/bin/activate
# ./manage.py runserver
```
Når du henter ændringer ned fra git skal du køre følgende kommando 
for at sikre din database er up to date:
```
# source virtualenv/bin/activate
# ./manage.py migrate
```


## Pull requests
Pull request er altid velkommen, følgende krav skal dog opfyldes. 
* [flake](http://flake8.pycqa.org/en/latest/) skal køres på koden. 
* Alle tests case skal lykkes
  

---
Mange editors kan sætte op til at informere dig om formatering problemer, 
alternativ kan du køre flake8 fra kommandolinjen manuelt
```
# flake8
```
  
Du kan tjekke om dig koden bryder nogle test cases passere ved at køre
```
# ./manage.py test
```
Hvis du har tilføjet ny funktionalitet må du meget gerne skrive unit tests af det

