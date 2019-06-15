from members.models.person import Person


def user_to_person(user):
    q = Person.objects.filter(user=user)
    if not q.exists():
        return None
    return q.get()
