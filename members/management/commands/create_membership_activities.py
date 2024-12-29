from django.core.management.base import BaseCommand
from members.models.union import Union
from members.models.activity import Activity
from members.models.activitytype import ActivityType
from members.models.department import Department
import datetime


class Command(BaseCommand):
    help = "Creates an activity pr. union to sign up for membership"
    output_transaction = True

    def handle(self, *args, **options):
        mainDepartment = Department.objects.get(pk=30)

        for curUnion in Union.objects.filter(closed_at__isnull=True):
            if curUnion.id == 1:
                print("springer over %s" % (curUnion.name))
                continue  # skip main union

            self.stdout.write("foreningen %s " % (curUnion.name))
            department = mainDepartment
            name = "Foreningsmedlemsskab 2025: %s" % (curUnion.name)
            open_hours = "-"

            localDepartments = str.join(
                ", ",
                Department.objects.filter(union=curUnion, closed_dtm=None).values_list(
                    "name", flat=True
                ),
            )

            try:
                department = Department.objects.get(name=curUnion.name)
            except Exception:
                print("Using backup main department at %s" % (curUnion.name))
                pass

            description = """Denne aktivitet er en særlig aktivitet oprettet for, at frivillige i Coding Pirates kan melde sig ind i vores forening og dermed få stemmeret i foreningen Coding Pirates %s samt Coding Pirates Denmark.

            Vær opmærksom på, at enkelte lokalforeninger ikke kræver, at frivillige er indmeldt som medlem for at have stemmeret, men for alle gælder, at man først har stemmeret i Coding Pirates Denmark, hvis man er meldt ind i sin lokalforening.

            Du behøver derfor IKKE tilmelde dig denne aktivitet, hvis du har et barn, der er medlem af Coding Pirates og som ønsker at deltage i en Coding Pirates aktivitet. (denne aktivitet giver IKKE adgang til klubaften eller andre aktiviteter).

            Ved at tilmelde dig denne aktivitet bliver du altså betalende medlem i foreningen Coding Pirates %s og kan dermed stemme til generalforsamlingen i din lokalforening og i hovedforeningen Coding Pirates Denmark.

            Flg. lokalafdelinger hører under %s:

            %s
            """ % (
                curUnion.name,
                curUnion.name,
                curUnion.name,
                localDepartments,
            )
            instructions = ""
            start_date = datetime.date(year=2025, month=1, day=1)
            end_date = datetime.date(year=2025, month=12, day=31)
            signup_closing = datetime.date(year=2025, month=12, day=31)
            open_invite = True
            price_in_dkk = 75
            max_participants = 9999
            max_age = 99
            min_age = 16
            activitytype = ActivityType.objects.get(id="FORENINGSMEDLEMSKAB")

            activity = Activity(
                activitytype=activitytype,
                department=department,
                union=curUnion,
                name=name,
                open_hours=open_hours,
                responsible_name=(
                    curUnion.chairman.name
                    if curUnion.chairman is not None
                    else curUnion.chairman_old
                ),
                responsible_contact=(
                    curUnion.chairman.email
                    if curUnion.chairman is not None
                    else curUnion.chairman_email_old
                ),
                address=curUnion.address,
                description=description,
                instructions=instructions,
                start_date=start_date,
                end_date=end_date,
                signup_closing=signup_closing,
                open_invite=open_invite,
                price_in_dkk=price_in_dkk,
                max_participants=max_participants,
                max_age=max_age,
                min_age=min_age,
                member_justified=True,
            )

            activity.save()
