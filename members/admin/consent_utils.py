from django.urls import reverse
from django.utils.html import format_html


def family_consent_link(family):
    """Link (new tab) to the public preview of the family's latest consent."""
    consent_id = family.get_consent_id()
    if consent_id is None:
        return "-"
    url = reverse("consent_preview", args=[consent_id])
    return format_html(
        '<a href="{}" target="_blank" rel="noopener">{}</a>', url, consent_id
    )
