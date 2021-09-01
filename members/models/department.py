from datetime import timedelta
from django.db import models
import members.models.emailtemplate
from members.models.activity import Activity
from django.utils import timezone


class Department(models.Model):
    class Meta:
        verbose_name_plural = "Afdelinger"
        verbose_name = "Afdeling"
        ordering = ["address__zipcode"]

    help_dept = """Vi tilføjer automatisk "Coding Pirates" foran navnet når vi
    nævner det de fleste steder på siden."""
    name = models.CharField("Navn", max_length=200, help_text=help_dept)
    description = models.TextField("Beskrivelse af afdeling", blank=True)
    open_hours = models.CharField("Åbningstid", max_length=200, blank=True)
    responsible_name = models.CharField("Afdelingsleder", max_length=200, blank=True)
    department_email = models.EmailField("E-mail", blank=True)
    department_leaders = models.ManyToManyField(
        "Person", limit_choices_to={"user__is_staff": True}, blank=True
    )
    address = models.ForeignKey("Address", on_delete=models.PROTECT)
    updated_dtm = models.DateTimeField("Opdateret", auto_now=True)
    created = models.DateField("Oprettet", blank=False, default=timezone.now)
    closed_dtm = models.DateField("Lukket", blank=True, null=True, default=None)
    isVisible = models.BooleanField("Kan ses på afdelingssiden", default=True)
    isOpening = models.BooleanField("Er afdelingen under opstart", default=False)
    website = models.URLField("Hjemmeside", blank=True)
    union = models.ForeignKey(
        "Union",
        verbose_name="Lokalforening",
        on_delete=models.PROTECT,
    )

    def no_members(self):
        return self.member_set.count()

    no_members.short_description = "Antal medlemmer"

    def __str__(self):
        return self.name

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
