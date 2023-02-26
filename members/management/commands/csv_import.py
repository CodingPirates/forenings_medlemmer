# -*- coding: utf-8 -*-
import csv
import datetime
from django.core.management.base import BaseCommand
from members.models import person, Family
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = "Imports CSV file with family addresses"
    output_transaction = True

    option_list = BaseCommand.option_list + (
        make_option(
            "-d",
            "--date_column",
            help="column which contains the date member has signed up. (First column is specified as 0)",
            type="int",
            default=0,
            metavar="column",
        ),
        make_option(
            "-e",
            "--email_column",
            help="column which contains the email of parent who has signed up. (First column is specified as 0)",
            type="int",
            default=4,
            metavar="column",
        ),
        make_option(
            "-n",
            "--name_column",
            help="column which contains the name of member who has signed up. (First column is specified as 0)",
            type="int",
            default=1,
            metavar="column",
        ),
        make_option(
            "-l",
            "--first_row_is_label",
            help="The first row in CSV file is expected to be column labels",
            action="store_true",
            default=False,
        ),
        make_option(
            "-f",
            "--date_format",
            help="Date format (look in sourcecode)",
            type="int",
            default=0,
            metavar="format",
        ),
    )
    args = "csvfile"

    def handle(self, *args, **options):
        if len(args) != 1:
            self.stdout.write("Invalid number of arguments")
            exit()

        try:
            csvfile = open(args[0], "r", encoding="utf-8")
        except IOError:
            self.stdout.write("Unable to open file: " + args[0])
            exit()

        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        entries = csv.reader(csvfile, dialect)
        columns = len(next(entries))
        csvfile.seek(0)
        entries = csv.reader(csvfile, dialect)

        if options["first_row_is_label"]:
            labels = next(entries)
        else:
            # make list of empty labels
            labels = []
            for col in range(columns):
                if col == options["date_column"]:
                    labels.append("Opskrivnings dato")
                elif col == options["email_column"]:
                    labels.append("e-mail")
                elif col == options["name_column"]:
                    labels.append("Navn")
                else:
                    labels.append("")

        datetimeobject = datetime.datetime.today()

        for entry in entries:
            email = entry[options["email_column"]].lower()
            name = entry[options["name_column"]].title().strip()

            if options["date_format"] == 0:
                date_format = "%m/%d/%Y %H:%M:%S %z"  # '3/20/2014 19:51:32'
                date = datetimeobject.strptime(
                    entry[options["date_column"]].lstrip() + " +0001", date_format
                )
            if options["date_format"] == 1:
                date_format = "%d. %m %Y, %H:%M %z"  # '12. december 2014, 17:58'
                months = [
                    ("januar", "1"),
                    ("februar", "2"),
                    ("marts", "3"),
                    ("april", "4"),
                    ("maj", "5"),
                    ("juni", "6"),
                    ("juli", "7"),
                    ("august", "8"),
                    ("september", "9"),
                    ("oktober", "10"),
                    ("november", "11"),
                    ("december", "12"),
                ]

                date_string = entry[options["date_column"]].lstrip()
                for month_name, month_number in months:
                    date_string = date_string.replace(month_name, month_number)
                date = datetimeobject.strptime(date_string + " +0001", date_format)

            # find or create the family
            family, created = Family.objects.get_or_create(email=email)

            # lookup person
            try:
                person = person.objects.get(name=name, family=family)  # noqa: F823
                # Ved ikke hvorfor den ikke ser person

                # if current waiting list is older, replace timestamp
                if date < person.added_at:
                    person.added_at = date
                    person.save()

            except ObjectDoesNotExist:
                # create the person
                person = person(
                    name=name, membertype=person.CHILD, family=family, added_at=date
                )
                person.save()
            except person.MultipleObjectsReturned:
                print(
                    "family "
                    + family.email
                    + " has duplicate mebers named "
                    + name
                    + " - signup date : "
                    + str(date)
                    + " not recorded"
                )
