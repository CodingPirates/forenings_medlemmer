from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from members.models.department import Department
from members.models.union import Union


@xframe_options_exempt
def departmentView(request, unique=None):
    depQuery = Department.objects.filter(closed_dtm__isnull=True).filter(isVisible=True)
    deps = {}
    for region in Union.regions:
        deps[region[1]] = []

    for department in depQuery:
        coordinates = (department.address.latitude, department.address.longitude)
        dep = {"html": department.toHTML(), "isVisible": department.isVisible}
        if None not in coordinates:
            dep["latitude"] = str(coordinates[0])
            dep["longtitude"] = str(coordinates[1])
        else:
            dep["isVisible"] = False
        deps[department.union.get_region_display()].append(dep)
    return render(request, "members/department_list.html", {"departments": deps})
