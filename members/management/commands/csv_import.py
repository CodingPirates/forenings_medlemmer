# -*- coding: utf-8 -*-
import csv
import datetime
from django.db import IntegrityError, transaction
from django.core.management.base import BaseCommand, CommandError
from members.models import Journal, Person, Family
from optparse import make_option
from  django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    help = 'Imports CSV file with family addresses'
    output_transaction = True

    option_list=BaseCommand.option_list + (
        make_option('-d', '--date_column', help="column which contains the date member has signed up. (First column is specified as 0)", type="int", default=0, metavar='column'),
        make_option('-e', '--email_column', help="column which contains the email of parent who has signed up. (First column is specified as 0)", type="int", default=4, metavar='column'),
        make_option('-n', '--name_column', help="column which contains the name of member who has signed up. (First column is specified as 0)", type="int", default=1, metavar='column'),
        make_option('-l', '--first_row_is_label', help="The first row in CSV file is expected to be column labels", action="store_true", default=False),
        )
    args = 'csvfile'

    def handle(self, *args, **options):

        if(len(args) != 1):
            self.stdout.write('Invalid number of arguments')
            exit()

        try:
            csvfile = open(args[0], 'r', encoding='utf-8')

        except:
            self.stdout.write('Unable to open file: ' + args[0])
            exit()

        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        entries = csv.reader(csvfile, dialect)
        columns = len(next(entries))
        csvfile.seek(0)
        entries = csv.reader(csvfile, dialect)

        if(options['first_row_is_label']):
            labels = next(entries)
        else:
            # make list of empty labels
            labels = []
            for col in range(columns):
                if(col == options['date_column']):
                    labels.append('Opskrivnings dato')
                elif (col == options['email_column']):
                    labels.append('e-mail')
                elif (col == options['name_column']):
                    labels.append('Navn')
                else:
                    labels.append('')


        datetimeobject = datetime.datetime.today()

        for entry in entries:

            email = entry[options['email_column']].lower()
            name = entry[options['name_column']].title().strip()

            journal = 'Importeret fra CSV fil:\n'
            for col in range(columns):
                journal = journal + labels[col] + ': ' + entry[col] + '\n'

            date = datetimeobject.strptime(entry[options['date_column']] + " +0001", '%m/%d/%Y %H:%M:%S %z')

            # find or create the family
            family, created = Family.objects.get_or_create(email = email)


            #lookup person
            try:
               person = Person.objects.get(name=name, family = family)

               # if current waiting list is older, replace timestamp
               if(date < person.added):
                   person.added = date
                   person.save()

            except ObjectDoesNotExist:
                # create the person
                person = Person(name=name, membertype=Person.CHILD, family = family, added = date)
                person.save()

            # store original data in log entry.
            logentry = Journal(family = family, person = person, body = journal)

            logentry.save
