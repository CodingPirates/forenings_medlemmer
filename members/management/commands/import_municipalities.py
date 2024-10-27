import csv
from django.core.management.base import BaseCommand
from members.models import Municipality

# run locally:
# docker compose run web ./manage.py import_municipalities members/management/commands/municipalities.csv


class Command(BaseCommand):
    help = "Import municipalities data from a CSV file into the Municipality model"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file containing municipalities data",
        )

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs["csv_file"]

        try:
            # Delete existing rows in Municipality model
            Municipality.objects.all().delete()
            self.stdout.write("Deleted all existing municipalities.")

            with open(csv_file_path, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file, delimiter=";")
                for row in reader:
                    name, address, zipcode, city, dawa_id = row
                    Municipality.objects.create(
                        name=name,
                        address=address,
                        zipcode=zipcode,
                        city=city,
                        dawa_id=dawa_id,
                    )
                    self.stdout.write(f"Added municipality: {name}")

            self.stdout.write(
                self.style.SUCCESS("Successfully imported all municipalities")
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f"File {csv_file_path} not found. Please check the file path."
                )
            )
