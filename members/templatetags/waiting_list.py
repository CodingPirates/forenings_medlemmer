from django import template
from members.models.waitinglist import WaitingList
from members.models.department import Department
from members.models.person import Person

register = template.Library()


@register.simple_tag
def number_on_waiting_list(row):
    return row.number_on_waiting_list()


@register.simple_tag
def already_on_waitinglist(person, department):
    if WaitingList.objects.filter(person=person, department=department):
        return True
    else:
        return False
