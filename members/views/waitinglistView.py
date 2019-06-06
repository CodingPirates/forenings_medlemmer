from django.shortcuts import render

from members.models.department import Department
from members.models.waitinglist import WaitingList
from django.contrib.auth.decorators import login_required


@login_required
def waitinglistView(request):
    unique = request.user.person.family.unique
    department_children_waiting = {"departments": {}}
    department_loop_counter = 0
    # deparments_query = Department.objects.filter(has_waiting_list = True).order_by('zipcode').filter(waitinglist__person__family__unique=unique)
    deparments_query = Department.objects.filter(
        has_waiting_list=True, closed_dtm=None
    ).order_by("zipcode")

    for department in deparments_query:
        department_children_waiting["departments"][department_loop_counter] = {}
        department_children_waiting["departments"][department_loop_counter][
            "name"
        ] = department.name
        department_children_waiting["departments"][department_loop_counter][
            "waiting"
        ] = {}

        waiting_in_department = (
            WaitingList.objects.filter(department__pk=department.pk)
            .select_related("person", "person__family")
            .order_by("on_waiting_list_since")
        )

        child_loop_counter = 1
        for waiting in waiting_in_department:
            department_children_waiting["departments"][department_loop_counter][
                "waiting"
            ][child_loop_counter] = {}
            if waiting.person.family.unique == unique:
                department_children_waiting["departments"][department_loop_counter][
                    "waiting"
                ][child_loop_counter]["firstname"] = waiting.person.firstname()
                department_children_waiting["departments"][department_loop_counter][
                    "waiting"
                ][child_loop_counter]["zipcode"] = waiting.person.zipcode
                department_children_waiting["departments"][department_loop_counter][
                    "waiting"
                ][child_loop_counter]["color"] = True
            else:
                department_children_waiting["departments"][department_loop_counter][
                    "waiting"
                ][child_loop_counter]["firstname"] = "-"
                department_children_waiting["departments"][department_loop_counter][
                    "waiting"
                ][child_loop_counter]["zipcode"] = waiting.person.zipcode
                department_children_waiting["departments"][department_loop_counter][
                    "waiting"
                ][child_loop_counter]["color"] = False

            department_children_waiting["departments"][department_loop_counter][
                "waiting"
            ][child_loop_counter]["added"] = waiting.person.added
            child_loop_counter = child_loop_counter + 1
        department_loop_counter = department_loop_counter + 1

    return render(
        request,
        "members/waitinglist.html",
        {"department_children_waiting": department_children_waiting, "unique": unique},
    )
