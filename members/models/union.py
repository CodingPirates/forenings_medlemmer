from django.db import models
from .payment import Payment
from .activity import Activity
from .person import Person
from .department import Department
from .activityparticipant import ActivityParticipant
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import timedelta
from django.db.models import F
import datetime


class Union(models.Model):
    class Meta:
        verbose_name_plural = "Foreninger"
        verbose_name = "Forening"
        ordering = ["name"]

    name = models.CharField("Foreningens navn", max_length=200)
    meeting_notes = models.URLField("Link til seneste referater", blank=True)
    founded = models.DateField("Stiftet")
    chairman = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        related_name="chairman",
        null=True,
        blank=True,
    )
    chairman_old = models.CharField("Formand", max_length=200, blank=True)
    chairman_email_old = models.EmailField("Formandens email", blank=True)
    second_chair = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="second_chair",
    )
    second_chair_old = models.CharField("Næstformand", max_length=200, blank=True)
    second_chair_email_old = models.EmailField("Næstformandens email", blank=True)
    cashier = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        related_name="cashier",
        null=True,
        blank=True,
    )
    cashier_old = models.CharField("Kasserer", max_length=200, blank=True)
    cashier_email_old = models.EmailField("Kassererens email", blank=True)
    secretary = models.ForeignKey(
        "Person",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretary",
    )
    secretary_old = models.CharField("Sekretær", max_length=200, blank=True)
    secretary_email_old = models.EmailField("Sekretærens email", blank=True)
    union_email = models.EmailField("Foreningens email", blank=True)
    statues = models.URLField("Link til gældende vedtægter", blank=True)
    founded = models.DateField("Stiftet", blank=True, null=True)
    address = models.ForeignKey("Address", on_delete=models.PROTECT)
    board_members = models.ManyToManyField("Person", blank=True)
    board_members_old = models.TextField("Menige medlemmer", blank=True)
    bank_main_org = models.BooleanField(
        "Sæt kryds hvis I har konto hos hovedforeningen (og ikke har egen bankkonto).",
        default=True,
    )
    bank_account = models.CharField(
        "Bankkonto:",
        max_length=15,
        blank=True,
        help_text="Kontonummer i formatet 1234-1234567890",
        validators=[
            RegexValidator(
                regex="^[0-9]{4} *?-? *?[0-9]{6,10} *?$",
                message="Indtast kontonummer i det rigtige format.",
            )
        ],
    )

    def __str__(self):
        return "Foreningen for " + self.name

    def clean(self):
        if self.bank_main_org is False and not self.bank_account:
            raise ValidationError(
                "Vælg om foreningen har konto hos hovedforeningen. Hvis ikke skal bankkonto udfyldes."
            )

    def members(self):
        years = range(self.founded.year, (timezone.now().date()).year + 1)
        members = {}
        departments = Department.objects.filter(union=self.id)
        for year in years:
            temp_members = []
            union_activities_1 = Activity.objects.filter(
                member_justified=True,
                department__in=departments,
                end_date__gt=F("start_date") + timedelta(days=2),
                start_date__year=year,
            )
            union_activities_2 = Activity.objects.filter(
                member_justified=True, union_id=self.id, start_date__year=year,
            ).union(union_activities_1)
            print("År")
            print(year)
            print("union_activities_1")
            print(union_activities_1)
            print("union_activities_2")
            print(union_activities_2)
            print("")
            for activity in union_activities_2:
                for participant in ActivityParticipant.objects.filter(
                    activity=activity
                ).distinct():
                    if (
                        len(
                            Payment.objects.filter(
                                person=participant.member.person,
                                amount_ore__gte=7500,
                                activity=activity,
                                confirmed_dtm__lte=make_aware(
                                    datetime.datetime(year, 9, 30)
                                ),
                                refunded_dtm__isnull=True,
                            )
                        )
                        > 0
                    ):
                        temp_members.append(participant.member.person)
            members[year] = Person.objects.filter().first()
            members[year] = temp_members
        return members

    def user_union_leader(self, user):
        people_on_board = [person.user for person in self.board_members.all()]
        board_posistions = [
            self.chairman,
            self.second_chair,
            self.cashier,
            self.secretary,
        ]
        board_posistions = [
            position.user for position in board_posistions if position is not None
        ]
        return user is not None and (
            user.is_superuser or user in people_on_board + board_posistions
        )
