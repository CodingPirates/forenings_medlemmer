from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from members.models import Department


@xframe_options_exempt
def departmentView(request, unique=None):
    return render(
        request,
        "members/department_list.html",
        {
            "skip_context": True,
            "departments": filter(
                lambda dep: dep.isVisible, Department.get_open_departments()
            ),
        },
    )
