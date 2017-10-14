from members.models.person import Person

def user_to_person(user):
    return Person.objects.filter(user=user).get()