from django.shortcuts import render
from members.models import (
    WaitingList,
    Department,
)
from members.utils.user import user_to_person

from members.utils.user import user_to_family
from django.contrib.auth.decorators import user_passes_test
from members.utils.user import is_not_logged_in_and_has_person

import requests


@user_passes_test(is_not_logged_in_and_has_person, "/admin_signup/")
def DepartmentSignup(request):
    departments = Department.get_open_departments()
    departments = [
        department for department in departments if department.address.region != ""
    ]
    children = []
    if request.user.is_authenticated:
        family = user_to_family(request.user)
        person = user_to_person(request.user)
        if person:
            if person.dawa_id == "":
                user_region = ""
            else:
                dawa_req = (
                    f"https://dawa.aws.dk/adresser/{person.dawa_id}?format=geojson"
                )
                try:
                    dawa_reply = requests.get(dawa_req).json()
                    user_region = dawa_reply["properties"]["regionsnavn"]
                except Exception:
                    user_region = ""
                    # and we simply skip the region, and sorting will be as default
            children = [
                {"person": child, "waitinglists": WaitingList.get_by_child(child)}
                for child in family.get_children().filter(anonymized=False)
            ]
            for child in children:
                child["departments_is_waiting"] = [
                    department for (department, _place) in child["waitinglists"]
                ]
                child["departments_not_waiting"] = [
                    department
                    for department in departments
                    if department not in child["departments_is_waiting"]
                ]
            departments_for_region_of_user = []
            departments_for_other_regions = []
            for department in departments:
                if department.address.region == user_region:
                    departments_for_region_of_user.append(department)
                else:
                    departments_for_other_regions.append(department)
            departments = departments_for_region_of_user + departments_for_other_regions
    return render(
        request,
        "members/department_signup.html",
        {"departments": departments, "children": children},
    )
