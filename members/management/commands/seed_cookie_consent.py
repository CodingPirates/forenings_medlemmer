from cookie_consent.models import Cookie, CookieGroup
from django.core.management.base import BaseCommand

_COOKIES = {
    "sessionid": (
        "Bruges til at holde dig logget ind, mens du bruger Medlemssystemet."
    ),
    "csrftoken": (
        "Bruges til at sikre, at det rent faktisk er dig, der indsender "
        "formularer på Medlemssystemet, og ikke en anden hjemmeside der "
        "forsøger at udgive sig for at være dig."
    ),
}


class Command(BaseCommand):
    help = "Create or update the 'necessary' cookie group used on the cookie declaration page"

    def handle(self, *args, **options):
        group, created = CookieGroup.objects.update_or_create(
            varname="necessary",
            defaults={
                "name": "Nødvendige cookies",
                "description": (
                    "Disse cookies er nødvendige for at Medlemssystemet kan "
                    "fungere, f.eks. til at holde dig logget ind. De kan "
                    "ikke fravælges."
                ),
                "is_required": True,
                "is_deletable": False,
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Created' if created else 'Updated'} 'necessary' cookie group"
            )
        )

        for name, description in _COOKIES.items():
            _, cookie_created = Cookie.objects.update_or_create(
                cookiegroup=group,
                name=name,
                domain="",
                defaults={"description": description},
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Added' if cookie_created else 'Updated'} cookie '{name}'"
                )
            )
