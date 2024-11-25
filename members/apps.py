from django.apps import AppConfig
from django.db.utils import OperationalError

class MembersConfig(AppConfig):
    name = 'members'

    def ready(self):
        from members.models.emailtemplate import EmailTemplate

        # Check if the NEW_VOLUNTEER email template exists, and create it if it does not
        try:
            if not EmailTemplate.objects.filter(idname="NEW_VOLUNTEER").exists():
                EmailTemplate.objects.create(
                    idname="NEW_VOLUNTEER",
                    name="Ny frivillig",
                    description="Email template for nye frivillig forespørgsler",
                    from_address="kontakt@codingpirates.dk",
                    subject="Ny frivillig til Coding Pirates {{ department }}",
                    body_html="<p>A new volunteer request has been made.</p><p>Details: {{ volunteer_request }}</p>",
                    body_text="A new volunteer request has been made.\nDetails: {{ volunteer_request }}",
                )
        except OperationalError:
            # Handle the case where the database is not ready yet
            pass