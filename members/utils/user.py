from members.models.family import Family
from members.models.person import Person


def user_to_person(user):
    try:
        return Person.objects.filter(user=user).get()
    except Person.DoesNotExist:
        return None


def user_to_family(user):
    try:
        return Family.objects.filter(person=user_to_person(user)).get()
    except Family.DoesNotExist:
        return None


def has_user(user):
    return user_to_person(user) is not None


def has_family(user):
    try:
        return user_to_family(user) is not None
    except Exception:
        return False


def is_not_logged_in_and_has_person(user):
    # Return True if user isnt logged in
    if not user.is_authenticated:
        return True
    # Return True if has a person else return false
    try:
        if has_user(user):
            return True
        else:
            return False
    except Exception:
        return False
