from django.db import models
from django.utils import timezone
from datetime import timedelta

from .season_participant import SeasonParticipant


def _default_sign_up_close():
    return timezone.now() + timedelta(days=30 * 1)


class WeekDays(models.IntegerChoices):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class Season(models.Model):
    class Meta:
        verbose_name_plural = "Sæsoner"
        verbose_name = "Sæson"
        ordering = ["department", "start_date"]

    name = models.CharField("Navn", max_length=200)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    start_time = models.TimeField("Start Tidspunkt")
    week_day = models
    end_time = models.TimeField("Slut Tidspunkt")
    responsible = models.ForeignKey("Person", on_delete=models.PROTECT)
    description = models.TextField("Beskrivelse", blank=False)
    instructions = models.TextField("Tilmeldings instruktioner", blank=True)
    start_date = models.DateField("Start dato")
    end_date = models.DateField("Slut dato")
    week_day = models.IntegerField(choices=WeekDays.choices)
    signup_closing = models.DateField(
        "Tilmelding lukker", default=_default_sign_up_close
    )
    open_invite = models.BooleanField("Fri tilmelding", default=False)
    price_in_dkk = models.DecimalField(
        "Pris",
        max_digits=10,
        decimal_places=2,
        default=500,
        help_text="Vi fratrækker automatisk 75 kr. til hovedforeningen",
    )
    max_participants = models.PositiveIntegerField("Max deltagere", default=30)
    max_age = models.PositiveIntegerField("Maximum Alder", default=17)
    min_age = models.PositiveIntegerField("Minimum Alder", default=7)

    def __str__(self):
        return self.department.name + ", " + self.name

    @staticmethod
    def get_open_seasons():
        today = timezone.now().date()
        active_seaons = Season.objects.filter(
            end_date__gte=today, signup_closing__gte=today, open_invite=True
        )
        return list(
            filter(
                lambda season: season.max_participants
                > SeasonParticipant.objects.filter(season=season).count(),
                active_seaons,
            )
        )
