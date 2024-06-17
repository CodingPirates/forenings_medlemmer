from dateutil.relativedelta import relativedelta
from django.utils import timezone


def check_is_person_too_young(activity, person):
    # Check for two things:
    # 1. if we are before start of activity: is person too young when activity starts ?
    # 2. if we are at or after activity starts: is person too young now ?
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
    # Check for two things:
    # 1. if we are before start of activity: is person too old  when activity starts ?
    # 2. if we are at or after activity starts: is person too old now ?

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
