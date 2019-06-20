from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import serializers

from members.models.department import Department
from members.models.union import Union
from members.models.person import Person
from members.models.waitinglist import WaitingList
from members.utils.user import user_to_person, has_user

import json


@login_required
@user_passes_test(has_user, '/admin_signup')
def departmentViewFamily(request, unique=None):
    depQuery = Department.objects.filter(closed_dtm__isnull=True).filter(isVisible=True)
    deps = {}
    for region in Union.regions:
        deps[region[1]] = []

    for department in depQuery:
        coordinates = department.getLatLon()
        dep = {
            'html': department.toHTML(),
            'onMap': department.onMap
        }
        if not(coordinates is None):
            dep['latitude'] = str(coordinates[0])
            dep['longtitude'] = str(coordinates[1])
        else:
            dep['onMap'] = False
        deps[department.union.get_region_display()].append(dep)

    # departments_json = json.dumps(list(Department.objects.all()))
    departments_json = serializers.serialize("json", depQuery)

    departments_json = []
    for row in json.loads(serializers.serialize("json", depQuery)):
        departments_json.append(row["fields"])

    family = user_to_person(request.user).family
    waiting_lists = WaitingList.objects.filter(person__family=family)
    children = family.person_set.filter(membertype=Person.CHILD)

    in_waiting_list = []
    for person in children:
        if waiting_lists.filter(person=person).exists():
            in_waiting_list.append(person)

    print(depQuery)

    return render(request, "members/departments_family.html", {
        'departments': depQuery,
        'children': children,
        'waiting_lists': waiting_lists,
        'in_waiting_list': in_waiting_list,
        'departments_json': json.dumps(departments_json)
    })
