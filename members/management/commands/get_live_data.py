from zipfile import ZipFile
import os
import json
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import DatabaseError
from members.models import Department, Union, Address, Person
from members.tests.factories import PersonFactory
import requests
import shutil

from .dump_public_data import MODELS_TO_DUMP as MODELS_TO_LOAD


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

        temp_dir = "live_data_dump"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        print("Downloading data File")
        response = requests.get(
            "http://members.codingpirates.dk/static/public_data.zip"
        )
        if response.status_code != 200:
            raise ConnectionError("Could not get zip file")

        print("Unzipping")
        with open(f"{temp_dir}/dump.zip", "wb+") as zip:
            zip.write(response.content)

        with ZipFile(f"{temp_dir}/dump.zip", "r") as zipObj:
            zipObj.extractall(temp_dir)

        with open(f"{temp_dir}/union.json", "r") as union_file:
            union_json = json.load(union_file)

        for union in union_json:
            union["fields"].pop("region", None)
            union["fields"].pop("REGION_CHOICES", None)
            _create_person_with_id(union["fields"]["chairman"])
            _create_person_with_id(union["fields"]["second_chair"])
            _create_person_with_id(union["fields"]["secretary"])
            _create_person_with_id(union["fields"]["cashier"])
            for board_member in union["fields"]["board_members"]:
                _create_person_with_id(board_member)

        with open(f"{temp_dir}/union.json", "w") as union_file:
            json.dump(union_json, union_file)

        with open(f"{temp_dir}/department.json", "r") as department_file:
            department_json = json.load(department_file)

        for department in department_json:
            for department_leader in department["fields"]["department_leaders"]:
                _create_person_with_id(department_leader)

        print("Reading dumps files")
        for model in MODELS_TO_LOAD:
            call_command("loaddata", f"{temp_dir}/{model}.json")

        # Remove temp dir
        shutil.rmtree(temp_dir)


def _create_person_with_id(id):
    if len(Person.objects.filter(pk=id)) == 0:
        return PersonFactory(pk=id)
