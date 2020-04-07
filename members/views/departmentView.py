from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from members.models.department import Department
from members.models.address import Address


@xframe_options_exempt
def departmentView(request, unique=None):
    departments = Department.get_open_departments()
    departments = [
        department
        for department in departments
        if department.address.region != ""
        and department.isVisible
        and None not in (department.address.latitude, department.address.longitude)
    ]
    return render(request, "members/department_list.html", {"departments": departments})
