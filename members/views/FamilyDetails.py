import datetime
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from members.models.activity import Activity
from members.models.activityinvite import ActivityInvite
from members.models.activityparticipant import ActivityParticipant
from members.models.department import Department
from members.models.person import Person
from members.models.waitinglist import WaitingList
from members.utils.user import user_to_person


@login_required
def FamilyDetails(request):

    family = user_to_person(request.user).family
    invites = ActivityInvite.objects.filter(
        person__family=family, expire_dtm__gte=timezone.now(), rejected_dtm=None
    )
    open_activities = Activity.objects.filter(
        open_invite=True, signup_closing__gte=timezone.now()
    ).order_by("zipcode")
    participating = ActivityParticipant.objects.filter(
        member__person__family=family
    ).order_by("-activity__start_date")
    departments_with_no_waiting_list = Department.objects.filter(has_waiting_list=False)
    waiting_lists = WaitingList.objects.filter(person__family=family)
    children = family.person_set.filter(membertype=Person.CHILD)
    ordered_persons = family.person_set.order_by("membertype").all()

    open_activities_with_persons = []
    # augment open invites with the persons who could join it in the family
    for curActivity in open_activities:
        applicablePersons = Person.objects.filter(
            family=family,  # only members of this family
            birthday__lte=timezone.now()
            - datetime.timedelta(days=curActivity.min_age * 365),  # old enough
            birthday__gt=timezone.now()
            - datetime.timedelta(days=curActivity.max_age * 365),  # not too old
        ).exclude(
            member__activityparticipant__activity=curActivity
        )  # not already participating

        if applicablePersons.exists():
            open_activities_with_persons.append(
                {
                    "id": curActivity.id,
                    "name": curActivity.name,
                    "department": curActivity.department,
                    "persons": applicablePersons,
                }
            )

    # update visited field
    family.last_visit_dtm = timezone.now()
    family.save()

    department_children_waiting = {"departments": {}}
    loop_counter = 0
    for department in Department.objects.filter(
        has_waiting_list=True, closed_dtm=None
    ).order_by("zipcode"):
        department_children_waiting["departments"][loop_counter] = {}
        department_children_waiting["departments"][loop_counter]["object"] = department
        department_children_waiting["departments"][loop_counter]["children_status"] = {}
        for child in children:
            department_children_waiting["departments"][loop_counter]["children_status"][
                child.pk
            ] = {}
            department_children_waiting["departments"][loop_counter]["children_status"][
                child.pk
            ]["object"] = child
            department_children_waiting["departments"][loop_counter]["children_status"][
                child.pk
            ]["firstname"] = child.firstname()
            department_children_waiting["departments"][loop_counter]["children_status"][
                child.pk
            ][
                "waiting"
            ] = False  # default not waiting
            for current_wait in waiting_lists:
                if (
                    current_wait.department == department
                    and current_wait.person == child
                ):
                    # child is waiting on this department
                    department_children_waiting["departments"][loop_counter][
                        "children_status"
                    ][child.pk]["waiting"] = True
                    break
        loop_counter = loop_counter + 1

    context = {
        "family": family,
        "invites": invites,
        "participating": participating,
        "open_activities": open_activities_with_persons,
        "need_confirmation": family.confirmed_dtm is None
        or family.confirmed_dtm
        < timezone.now()
        - datetime.timedelta(days=settings.REQUEST_FAMILY_VALIDATION_PERIOD),
        "request_parents": family.person_set.exclude(membertype=Person.CHILD).count()
        < 1,
        "department_children_waiting": department_children_waiting,
        "departments_with_no_waiting_list": departments_with_no_waiting_list,
        "children": children,
        "ordered_persons": ordered_persons,
    }
    return render(request, "members/family_details.html", context)
