from members.models.person import Person
from django.http import Http404


def user_to_person(user):
    q = Person.objects.filter(user=user)
    if not q.exists():
        raise Http404("User doesn't have an associated Person")
    return q.get()
