import os

from django.core.management.base import BaseCommand

from members.tests.factories import PayableItemFactory
from members.models import PayableItem


email_dir = "generated_emails"


class Command(BaseCommand):
    help = "Renders emails with test data"

    def handle(self, *args, **options):
        if not os.path.exists(email_dir):
            os.makedirs(email_dir)

        _write_payment_confirmation()


def _write_payment_confirmation():
    payment = PayableItemFactory.build()
    html, text = PayableItem._render_payment_confirmation(payment)
    with open(f"{email_dir}/payment_confirmed_email.html", "w+") as htmlFile:
        htmlFile.write(html)
    with open(f"{email_dir}/payment_confirmed_email.txt", "w+") as txtFile:
        txtFile.write(text)
