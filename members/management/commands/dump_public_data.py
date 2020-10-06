import zipfile
import json
from io import StringIO

from django.core.management.base import BaseCommand
from django.core.management import call_command

MODELS_TO_DUMP = ["address", "union", "department", "emailtemplate", "activity"]


class Command(BaseCommand):
    help = "Dumps public data to zip file"

    def handle(self, *args, **options):
        save_dump(get_dump())


def get_dump():
    dumps = {}
    for model in MODELS_TO_DUMP:
        dump = StringIO()
        call_command("dumpdata", f"members.{model}", format="json", stdout=dump)
        dumps[model] = json.loads(dump.getvalue())

    public_addresses = [
        department_info["fields"]["address"] for department_info in dumps["department"]
    ]
    public_addresses += [
        union_info["fields"]["address"] for union_info in dumps["union"]
    ]
    dumps["address"] = [
        address for address in dumps["address"] if address["pk"] in public_addresses
    ]

    for department in dumps["department"]:
        department["fields"]["department_leaders"] = []
    return dumps


def save_dump(dump):
    with zipfile.ZipFile(
        "members/static/public_data.zip", "w", compression=zipfile.ZIP_DEFLATED
    ) as zip:
        for model in MODELS_TO_DUMP:
            with zip.open(f"{model}.json", "w") as jsonFile:
                jsonFile.write(json.dumps(dump[model], indent=4).encode())
