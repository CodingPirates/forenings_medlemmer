import zipfile
import json
from io import StringIO
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import DatabaseError
from members.models import Department, Union, Address
import requests

MODELS_TO_LOAD = ["department", "union", "address"]


class Command(BaseCommand):
    help = "Gets public data and loads it into the system"

    def handle(self, *args, **options):
        in_database = (
            len(Department.objects.all()),
            len(Union.objects.all()),
            len(Address.objects.all()),
        )
        if in_database != (0, 0, 0):
            raise DatabaseError(
                "Du forsøgte at indsætte data i en ikke tom database. Det må man ikke "
            )

        temp_dir = "temp_dump"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        get_dump(temp_dir)
        # load_data(temp_dir)
        # delete_data(temp_dir)


def get_dump(dir):
    response = requests.get(
        "http://medlemssystem-staging.herokuapp.com/static/public_data.zip"
    )
    if response.status_code != 200:
        raise ConnectionError("Could not get zip file")
    zip = zipfile.ZipFile(response.content)
    print(zip)
