from django.shortcuts import render
from members.models import (
    WaitingList,
    Department,
)

from members.utils.user import user_to_family
from django.contrib.auth.decorators import user_passes_test
from members.utils.user import is_not_logged_in_and_has_person


@user_passes_test(is_not_logged_in_and_has_person, "/admin_signup/")
def DepartmentSignup(request):
    departments = Department.get_open_departments()
    departments = [
        department for department in departments if department.address.region != ""
    ]
    children = []
    if request.user.is_authenticated:
        family = user_to_family(request.user)
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
    return render(
        request,
        "members/department_signup.html",
        {"departments": departments, "children": children},
    )
