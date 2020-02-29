from django.contrib import admin
from members.models import Department


class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "department",
        "start_date",
        "open_invite",
        "price_in_dkk",
        "max_participants",
    )
    date_hierarchy = "start_date"
    search_fields = ("name", "department__name")
    list_per_page = 20
    raw_id_fields = ("department",)
    list_filter = ("department", "open_invite")
    save_as = True

    # Only view activities on own department
    def get_queryset(self, request):
        qs = super(ActivityAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        departments = Department.objects.filter(adminuserinformation__user=request.user)
        return qs.filter(department__in=departments)

    # Only show own departments when creating new activity
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department" and not request.user.is_superuser:
            kwargs["queryset"] = Department.objects.filter(
                adminuserinformation__user=request.user
            )
        return super(ActivityAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    fieldsets = (
        ("Afdeling", {"fields": ("department",)}),
        (
            "Aktivitet",
            {
                "description": "<p>Aktivitetsnavnet skal afspejle aktivitet samt tidspunkt. F.eks. <em>Forårssæson 2018</em>.</p><p>Tidspunkt er f.eks. <em>Onsdage 17:00-19:00</em></p>",
                "fields": (
                    "name",
                    "open_hours",
                    "description",
                    "start_date",
                    "end_date",
                    "member_justified",
                ),
            },
        ),
        (
            "Lokation og ansvarlig",
            {
                "description": "<p>Adresse samt ansvarlig kan adskille sig fra afdelingens informationer (f.eks. et gamejam der foregår et andet sted).</p>",
                "fields": (
                    "responsible_name",
                    "responsible_contact",
                    "streetname",
                    "housenumber",
                    "floor",
                    "door",
                    "zipcode",
                    "city",
                    "placename",
                ),
            },
        ),
        (
            "Tilmeldingsdetaljer",
            {
                "description": '<p>Tilmeldingsinstruktioner er tekst der kommer til at stå på betalingsformularen på tilmeldingssiden. Den skal bruges til at stille spørgsmål, som den, der tilmelder sig, kan besvare ved tilmelding.</p><p>Fri tilmelding betyder, at alle, når som helst kan tilmelde sig denne aktivitet - efter "først til mølle"-princippet. Dette er kun til arrangementer og klubaften-sæsoner i områder, hvor der ikke er nogen venteliste. Alle arrangementer med fri tilmelding kommer til at stå med en stor "tilmeld" knap på medlemssiden. <b>Vi bruger typisk ikke fri tilmelding - spørg i Slack hvis du er i tvivl!</b></p>',
                "fields": (
                    "instructions",
                    "open_invite",
                    "price_in_dkk",
                    "signup_closing",
                    "max_participants",
                    "min_age",
                    "max_age",
                ),
            },
        ),
    )
