from members.models.person import Person

from django.core.exceptions import ObjectDoesNotExist


def user_to_person(user):
    try:
        return Person.objects.filter(user=user).get()
    except Person.DoesNotExist:
        return None

def has_user(user):
    person = user_to_person(user)
    if person == None:
        return False
    else:
        return True