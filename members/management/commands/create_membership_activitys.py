from django.db import IntegrityError, transaction
from django.core.management.base import BaseCommand, CommandError
from members.models import Union, Activity, Department
import datetime

class Command(BaseCommand):
    help = 'Creates an activity pr. union to sign up for membership'
    output_transaction = True

    def handle(self, *args, **options):
        mainDepartment = Department.objects.get(pk=30)

        for curUnion in Union.objects.all():
            self.stdout.write("foreningen %s " % (curUnion.name))
            department = mainDepartment
            name = "Forenings medlemskab: %s" % (curUnion.name)
            open_hours = "-"
            #responsible_name = "Coding Pirates"
            #responsible_contact = "kontakt@codingpirates.dk"
            #placename = ""
            #zipcode = "5000"
            #city = "Odense"
            #streetname = "Seebladsgade"
            #housenumber = "1"
            #floor = ""
            #door = ""
            dawa_id = ""

            localDepartments = str.join(", ", Department.objects.filter(union=curUnion).values_list("name", flat=True))
            description = """Denne aktivitet er en særlig aktivitet oprettet for at kunne tilmelde sig som medlem med stemmeret i foreningen Coding Pirates

            Du behøver IKKE tilmelde dig denne aktivitet hvis
            1: Du har et barn der ønsker at deltage i en Coding Pirates aktivitet. (denne aktivitet giver ikke adgang til klubaften eller andre aktiviteter)
            2: Du ønsker at stemme som værge for dit barn, der allerede er tilmeldt klubaften.
            
            Hvis dit barn er medlem af foreningen (tilmeldt og betalt for ugentlig klubaktivitet) kan du stemme på barnets vejne ved at tilmelde barnet til aktiviteten "fuldmagt ved general forsamling".
            
            Ved at tilmelde dig denne aktivitet, bliver du betalende medlem i foreningen Coding Pirates %s og kan dermed stemme til general forsamlingen.
            
            Flg. lokalafdelinger hører under %s:
            
            %s
            """ % (curUnion.name, curUnion.name, localDepartments)

            instructions = ""
            start_date = datetime.date(year=2018, month=1, day=1)
            end_date = datetime.date(year=2018, month=12, day=31)
            signup_closing = datetime.date(year=2018, month=4, day=1)
            open_invite = True
            price_in_dkk = 75
            max_participants = 9999
            max_age = 99
            min_age = 16

            activity = Activity(department = department,
                                name=name,
                                open_hours = open_hours,
                                responsible_name = curUnion.chairman,
                                responsible_contact = curUnion.chairman_email,
                                placename = curUnion.placename,
                                zipcode = curUnion.zipcode,
                                city = curUnion.city,
                                streetname = curUnion.streetname,
                                housenumber = curUnion.housenumber,
                                floor = curUnion.floor,
                                door = curUnion.door,
                                dawa_id = dawa_id,
                                description = description,
                                instructions = instructions,
                                start_date = start_date,
                                end_date = end_date,
                                signup_closing = signup_closing,
                                open_invite = open_invite,
                                price_in_dkk = price_in_dkk,
                                max_participants = max_participants,
                                max_age = max_age,
                                min_age = min_age
                                )

            activity.save()