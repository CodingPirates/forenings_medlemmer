from django.conf import settings
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from members.models import EmailTemplate


VOLUNTEER_USER_CONFIRMATION_TEMPLATE_ID = "VOLUNTEER_USER_CONFIRMATION"


def ensure_volunteer_user_confirmation_template():
    try:
        return EmailTemplate.objects.get(idname=VOLUNTEER_USER_CONFIRMATION_TEMPLATE_ID)
    except EmailTemplate.DoesNotExist:
        body_html = "<h2>Bekræft din nye frivilligrolle</h2>\n"
        body_html += "<p>Hej {{ person.name }},</p>\n"
        body_html += "<p>En administrator har oprettet en ny frivilligrolle til dig hos Coding Pirates.</p>\n"
        body_html += (
            "<p><strong>Afdeling:</strong> {{ volunteer.department.name }}<br>\n"
        )
        body_html += "<strong>Aktivitet:</strong> {% if volunteer.activity %}{{ volunteer.activity.name }}{% else %}Generel frivillig{% endif %}<br>\n"
        body_html += "<strong>Startdato:</strong> {% if volunteer.start_date %}{{ volunteer.start_date|date:'Y-m-d' }}{% else %}-{% endif %}</p>\n"
        body_html += '<p>Bekræft eller afvis rollen på <a href="{{ volunteer_confirmation_url }}">din frivilligside</a>.</p>\n'
        body_html += '<p>Hvis du ikke allerede er logget ind, kan du først logge ind her: <a href="{{ volunteer_login_url }}">{{ volunteer_login_url }}</a>.</p>\n'
        body_html += "<p>Med venlig hilsen<br>Coding Pirates Danmark</p>"

        body_text = "Bekræft din nye frivilligrolle\n\n"
        body_text += "Hej {{ person.name }},\n\n"
        body_text += "En administrator har oprettet en ny frivilligrolle til dig hos Coding Pirates.\n\n"
        body_text += "Afdeling: {{ volunteer.department.name }}\n"
        body_text += "Aktivitet: {% if volunteer.activity %}{{ volunteer.activity.name }}{% else %}Generel frivillig{% endif %}\n"
        body_text += "Startdato: {% if volunteer.start_date %}{{ volunteer.start_date|date:'Y-m-d' }}{% else %}-{% endif %}\n\n"
        body_text += "Bekræft eller afvis rollen på din frivilligside: {{ volunteer_confirmation_url }}\n"
        body_text += "Hvis du ikke allerede er logget ind, kan du først logge ind her: {{ volunteer_login_url }}\n\n"
        body_text += "Med venlig hilsen\nCoding Pirates Danmark"

        return EmailTemplate.objects.create(
            idname=VOLUNTEER_USER_CONFIRMATION_TEMPLATE_ID,
            name="Bekræft frivilligrolle",
            description="Email til brugeren når en administrator opretter en ny frivilligrolle, som skal bekræftes.",
            subject="Bekræft din frivilligrolle hos Coding Pirates",
            from_address="kontakt@codingpirates.dk",
            body_html=body_html,
            body_text=body_text,
            template_help="Tilgængelige variable: person, volunteer, volunteer_confirmation_url, volunteer_login_url",
        )


def send_volunteer_user_confirmation_email(volunteer):
    template = ensure_volunteer_user_confirmation_template()
    confirmation_url = (
        f"{settings.BASE_URL}{reverse('volunteer_signup')}"
        "#pending-volunteer-confirmations"
    )
    login_url = (
        f"{settings.BASE_URL}{reverse('person_login')}"
        f"?next={reverse('volunteer_signup')}"
    )
    context = {
        "volunteer": volunteer,
        "department": volunteer.department,
        "activity": volunteer.activity,
        "person": volunteer.person,
        "volunteer_confirmation_url": confirmation_url,
        "volunteer_login_url": login_url,
    }
    return template.makeEmail([volunteer.person], context, allow_multiple_emails=True)


def log_volunteer_user_confirmation_change(request, volunteer, old_status, new_status):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return

    if old_status == new_status:
        return

    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(volunteer).pk,
        object_id=volunteer.pk,
        object_repr=str(volunteer),
        action_flag=CHANGE,
        change_message=(
            f"Brugerbekræftelse ændret fra '{old_status}' til '{new_status}'."
        ),
    )
