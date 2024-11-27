from django.apps import AppConfig
from django.db.utils import OperationalError


class MembersConfig(AppConfig):
    name = "members"

    def ready(self):
        from members.models.emailtemplate import EmailTemplate

        # Check if email templates exists, and create them if they do not
        try:
            if not EmailTemplate.objects.filter(idname="NEW_VOLUNTEER").exists():
                EmailTemplate.objects.create(
                    idname="NEW_VOLUNTEER",
                    name="Ny frivillig",
                    description="Ny frivillig forespørgsel",
                    from_address="kontakt@codingpirates.dk",
                    subject="Ny frivillig til Coding Pirates {{ department }}",
                    body_html="""
                        <p>Se detaljer i medlemssystemet, under Admin</p>""",
                    body_text="""
                        Se detaljer i medlemssystemet, under Admin""",
                )

            if not EmailTemplate.objects.filter(idname="SECURITY_TOKEN").exists():
                EmailTemplate.objects.create(
                    idname="SECURITY_TOKEN",
                    name="Security Token",
                    description="Sikkerhedskode",
                    from_address="kontakt@codingpirates.dk",
                    subject="Sikkerhedskode for Coding Pirates",
                    body_html="<p>Din sikkerhedskode er: {{ token }}</p>",
                    body_text="Din sikkerhedskode er: {{ token }}",
                )

        except OperationalError:
            # Handle the case where the database is not ready yet
            pass
