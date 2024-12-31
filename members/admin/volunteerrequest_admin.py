from django.contrib import admin


class VolunteerRequestAdmin(admin.ModelAdmin):
    list_display = (
        "get_name",
        "get_email",
        "get_phone",
        "get_age",
        "get_new",
        "created",
        "finished",
    )

    date_hierarchy = "created"

    readonly_fields = (
        "get_name",
        "get_email",
        "get_phone",
        "get_age",
        "get_new",
        "created",
        "finished",
        "info_whishes",
        "info_reference",
    )

    fieldsets = [
        (
            "Person data",
            {
                "fields": ("get_name", "get_email", "get_phone", "get_age", "get_new"),
            },
        ),
        (
            "Ønsker og referencer",
            {
                "fields": ("info_whishes", "info_reference"),
            },
        ),
    ]

    def get_name(self, obj):
        if obj.person is None:
            return obj.name
        else:
            return obj.person.name

    get_name.short_description = "Navn"

    def get_email(self, obj):
        if obj.person is None:
            return obj.email
        else:
            return obj.person.email

    get_email.short_description = "Email"

    def get_phone(self, obj):
        if obj.person is None:
            return obj.phone
        else:
            return obj.person.phone

    get_phone.short_description = "Telefon"

    def get_age(self, obj):
        if obj.person is None:
            return obj.age
        else:
            return obj.person.age_years()

    get_age.short_description = "Alder"

    def get_new(self, obj):
        return obj.person is None

    get_new.short_description = "Ny ?"
    get_new.boolean = True
