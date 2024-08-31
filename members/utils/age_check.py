from dateutil.relativedelta import relativedelta
from django.utils import timezone


def check_is_person_too_young(activity, person):
    # Check for three things:
    # 1. Does the person have a birthday set (if none, then return false)
    # 2. if we are before start of activity: is person too young when activity starts ?
    # 3. if we are at or after activity starts: is person too young now ?

    if person.birthday is None:
        return True

    if timezone.now().date() <= activity.start_date:
        return (
            person.birthday + relativedelta(years=activity.min_age)
            > activity.start_date
        )
    else:
        return (
            person.birthday + relativedelta(years=activity.min_age)
            > timezone.now().date()
        )


def check_is_person_too_old(activity, person):
    # Check for three things:
    # 1. Does the person have a birthday set (if none, then return false)
    # 2. if we are before start of activity: is person too old  when activity starts ?
    # 3. if we are at or after activity starts: is person too old now ?

    if person.birthday is None:
        return True

    if timezone.now().date() <= activity.start_date:
        return (
            person.birthday + relativedelta(years=activity.max_age + 1, days=-1)
            < activity.start_date
        )
    else:
        return (
            person.birthday + relativedelta(years=activity.max_age + 1, days=-1)
            < timezone.now().date()
        )
