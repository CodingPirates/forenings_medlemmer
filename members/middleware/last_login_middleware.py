from django.utils import timezone

from members.models import Person


class LastLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            family = Person.objects.get(user=request.user).family
            family.last_visit_at = timezone.now()
            family.save()
