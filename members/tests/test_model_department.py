from datetime import timedelta, date
from random import randint
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from members.forms import vol_emailForm
from members.models import Department, EmailTemplate, EmailItem
from .factories import DepartmentFactory, ActivityFactory


class TestModelDepartment(TestCase):
    def setUp(self):
        self.department = DepartmentFactory(closed_dtm=None)
        self.template = EmailTemplate(
            idname="VOL_NEW_DEP_HEAD",
            name="Email til afdelingslederen ved ny frivillig",
            description="Ny frivillig notifikation til afdelingskaptajnen",
            subject="Ny frivillig",
            body_html="Just a test",
            body_text="Just a test",
        )
        self.template.save()

    def test_get_open_departments(self):
        open_departments = DepartmentFactory.create_batch(10, closed_dtm=None)
        [
            ActivityFactory.create(
                start_date=timezone.now(),
                end_date=timezone.now() - timedelta(days=randint(0, 350)),
                department=department,
            )
            for department in open_departments
        ]
        # Department young than a year and no activities
        new_departments = DepartmentFactory.create_batch(
            10,
            closed_dtm=None,
            created=timezone.now() - timedelta(days=randint(0, 350)),
        )
        expected = set(open_departments + new_departments)

        # Closed departments
        DepartmentFactory.create_batch(10, closed_dtm=timezone.now())

        # depatments older than a year not closed but no activities in the
        # last year or nor activites at all
        old_departments = DepartmentFactory.create_batch(
            10,
            closed_dtm=None,
            created=timezone.now() - timedelta(days=randint(367, 999)),
        )
        [
            ActivityFactory.create(
                end_date=timezone.now() - timedelta(days=randint(367, 999)),
                department=department,
            )
            for department in old_departments[:5]
        ]

        self.assertEqual(expected, set(Department.get_open_departments()))

    def test_send_new_volunteer(self):
        email_amount = len(mail.outbox)
        department = Department.objects.get(pk=self.department.pk)
        form = vol_emailForm(
            data={
                "form_id": "vol_email",
                "volunteer_email": "test@test.dk",
                "volunteer_name": "Åse",
                "volunteer_zipcode": 4100,
                "volunteer_city": "Ringsted",
                "volunteer_phone": 11223344,
                "volunteer_birthday": date.today()
                - timedelta(days=randint(7305, 12784)),
                "volunteer_department": self.department.pk,
            }
        )
        if form.is_valid():
            department.new_volunteer_email_dep_head(form)
        email_amount += 1
        call_command("runcrons")
        self.assertEqual(len(mail.outbox), email_amount)
