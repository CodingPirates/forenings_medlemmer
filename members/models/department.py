from datetime import timedelta
from django.db import models
import members.models.emailtemplate
from members.models.activity import Activity
from members.models.waitinglist import WaitingList
from django.utils import timezone


class Department(models.Model):
    class Meta:
        verbose_name_plural = "Afdelinger"
        verbose_name = "Afdeling"
        ordering = ["address__zipcode"]
        permissions = (("view_all_departments", "Can view all Afdelinger"),)

    help_dept = """Vi tilføjer automatisk "Coding Pirates" foran navnet når vi
    nævner det de fleste steder på siden."""
    name = models.CharField("Navn", max_length=200, help_text=help_dept)
    description = models.TextField("Beskrivelse af afdeling", blank=True)
    open_hours = models.CharField("Åbningstid", max_length=200, blank=True)
    responsible_name = models.CharField("Afdelingsleder", max_length=200, blank=True)
    department_email = models.EmailField("E-mail", blank=True)
    department_leaders = models.ManyToManyField(
        "Person",
        limit_choices_to={"user__is_staff": True},
        blank=True,
        verbose_name="Afdelingsledere",
    )
    address = models.ForeignKey(
        "Address", on_delete=models.PROTECT, verbose_name="Adresse"
    )
    has_waiting_list = models.BooleanField("Brug af venteliste", default=True)
    updated_dtm = models.DateTimeField("Opdateret", auto_now=True)
    created = models.DateField(
        "Oprettet",
        blank=False,
        default=timezone.now,
        help_text="Dato for oprettelse af denne afdeling",
    )
    closed_dtm = models.DateField(
        "Lukket",
        blank=True,
        null=True,
        default=None,
        help_text="Dato for lukning af denne afdeling",
    )
    isVisible = models.BooleanField(
        "På afdelingskort",
        default=True,
        help_text="Bliver denne afdeling vist på https://codingpirates.dk/afdelinger/ ?",
    )
    isOpening = models.BooleanField(
        "Under opstart", default=False, help_text="Er denne afdeling under opstart ?"
    )
    website = models.URLField("Hjemmeside", blank=True)
    union = models.ForeignKey(
        "Union",
        verbose_name="Lokalforening",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return self.name

    def waitinglist_count(self):
        return WaitingList.objects.filter(department=self).count()

    def new_volunteer_email(self, volunteer_name):
        # First fetch department leaders email
        new_vol_email = members.models.emailtemplate.EmailTemplate.objects.get(
            idname="VOL_NEW"
        )
        context = {"department": self, "volunteer_name": volunteer_name}
        new_vol_email.makeEmail(self, context)

    @staticmethod
    def get_open_departments():
        result = []
        a_year_ago = (timezone.now() - timedelta(days=366)).date()
        for department in Department.objects.filter(closed_dtm=None).order_by(
            "address__region", "name"
        ):
            department_activties = Activity.objects.filter(
                department=department
            ).order_by("-end_date")
            if a_year_ago < department.created:
                result.append(department)
            elif (
                len(department_activties) > 0
                and a_year_ago < department_activties[0].end_date
            ):
                result.append(department)

        return result
