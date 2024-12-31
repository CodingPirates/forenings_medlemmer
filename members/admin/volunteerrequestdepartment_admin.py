from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from django import forms

from members.models import (
    VolunteerRequestDepartment,
    Department,
    AdminUserInformation,
    Activity,
    Volunteer,
)


class VolunteerRequestDepartmentListFilter(admin.SimpleListFilter):
    title = "Afdelinger"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        departments = []
        for d in (
            Department.objects.filter(
                volunteerrequestdepartment__department__in=AdminUserInformation.get_departments_admin(
                    request.user
                )
            )
            .order_by("name")
            .distinct()
        ):
            departments.append((str(d.pk), str(d)))
        return departments

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(department__pk=self.value)


class VolunteerRequestDepartmentAdminForm(forms.ModelForm):
    class Meta:
        model = VolunteerRequestDepartment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "department" in self.data:
            try:
                department_id = int(self.data.get("department"))
                self.fields["activity"].queryset = Activity.objects.filter(
                    department_id=department_id
                ).order_by("name")
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Activity queryset
        elif self.instance.pk:
            self.fields["activity"].queryset = (
                self.instance.department.activity_set.order_by("name")
            )


class VolunteerRequestDepartmentAdmin(admin.ModelAdmin):
    form = VolunteerRequestDepartmentAdminForm

    list_display = (
        "volunteer_request",
        "get_new",
        "department",
        "activity",
        "created",
        "finished",
        "status",
        "whishes",
        "reference",
    )

    date_hierarchy = "created"

    readonly_fields = (
        "get_new",
        "department",
        "activity",
        "whishes",
        "reference",
        "get_volunteer_request_name",
        "get_volunteer_request_email",
        "get_volunteer_request_phone",
    )

    list_filter = (
        VolunteerRequestDepartmentListFilter,
        "status",
    )

    fieldsets = [
        (
            "Forespørgsel",
            {
                "description": "Information fra person om at blive frivillig",
                "fields": (
                    "get_volunteer_request_name",
                    "get_volunteer_request_email",
                    "get_volunteer_request_phone",
                    "department",
                    "activity",
                    "whishes",
                    "reference",
                ),
            },
        ),
        (
            "Dato og status",
            {
                "description": "Information om oprettelse og status",
                "fields": ("created", "finished", "status"),
            },
        ),
    ]

    actions = ["process_volunteer_request"]

    class Media:
        js = ("members/js/admin.js",)

    def process_volunteer_request(self, request, queryset):
        for obj in queryset:
            if obj.volunteer_request.person:
                # Create Volunteer record
                Volunteer.objects.create(
                    person=obj.volunteer_request.person,
                    department=obj.department,
                    activity=obj.activity,
                )
                # Update status to 4 (Aktiv)
                obj.status = 4
                obj.save()
                self.message_user(
                    request,
                    f"Volunteer record created for {obj.volunteer_request.person.name}",
                )
            else:
                # Send email with link to create user
                token = obj.volunteer_request.token
                create_user_url = request.build_absolute_uri(
                    reverse("create_user", args=[token])
                )
                email_body = f"Please create a user by clicking the following link: {create_user_url}"
                send_mail(
                    "Create User for Volunteer Request",
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.volunteer_request.email],
                )
                self.message_user(
                    request,
                    f"Email sent to {obj.volunteer_request.email} with link to create user",
                )

    process_volunteer_request.short_description = "Process Volunteer Request"

    def get_new(self, obj):
        return obj.volunteer_request.person is None

    get_new.short_description = "Ny ?"
    get_new.boolean = True

    def get_volunteer_request_name(self, obj):
        if obj.volunteer_request.person is None:
            return obj.volunteer_request.name
        else:
            return obj.volunteer_request.person.name

    get_volunteer_request_name.short_description = "Navn"

    def get_volunteer_request_email(self, obj):
        if obj.volunteer_request.person is None:
            return obj.volunteer_request.email
        else:
            return obj.volunteer_request.person.email

    get_volunteer_request_email.short_description = "Email"

    def get_volunteer_request_phone(self, obj):
        if obj.volunteer_request.person is None:
            return obj.volunteer_request.phone
        else:
            return obj.volunteer_request.person.phone

    get_volunteer_request_phone.short_description = "Telefon"

    def whishes(self, obj):
        return format_html("<br>".join(obj.volunteer_request.info_whishes.splitlines()))

    whishes.short_description = "Ønsker"

    def reference(self, obj):
        return format_html(
            "<br>".join(obj.volunteer_request.info_reference.splitlines())
        )

    reference.short_description = "Referencer"
