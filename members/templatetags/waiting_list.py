from django import template
from members.models.waitinglist import WaitingList

register = template.Library()


@register.simple_tag
def number_on_waiting_list(row):
    return row.number_on_waiting_list()
