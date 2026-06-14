from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django import forms

from members.models import (
    VolunteerRequestItem,
    Department,
    AdminUserInformation,
    Activity,
    Volunteer,
)

from members.models.emailtemplate import EmailTemplate


class VolunteerRequestItemListFilter(admin.SimpleListFilter):
    title = "Afdelinger"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        departments = []
        for d in (
            Department.objects.filter(
                volunteerrequestitem__department__in=AdminUserInformation.get_departments_admin(
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
            return queryset.filter(department__pk=self.value())


class VolunteerRequestItemAdminForm(forms.ModelForm):
    class Meta:
        model = VolunteerRequestItem
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
                self.fields["activity"].queryset = Activity.objects.none()
        elif self.instance.pk and self.instance.department:
            self.fields["activity"].queryset = (
                self.instance.department.activity_set.order_by("name")
            )
        else:
            self.fields["activity"].queryset = Activity.objects.none()
        # super().__init__(*args, **kwargs)
        # if "department" in self.data:
        #     try:
        #         department_id = int(self.data.get("department"))
        #         self.fields["activity"].queryset = Activity.objects.filter(
        #             department_id=department_id
        #         ).order_by("name")
        # #     except (ValueError, TypeError):
        # #         self.fields["activity"].queryset = Activity.objects.none()
        # # elif self.instance.pk and self.instance.activity is not None:
        # #     self.fields["activity"].queryset = self.instance.department.activity_set.order_by("name")
        # # else:
        # #     self.fields["activity"].queryset = Activity.objects.none()

        # # if "department" in self.data:
        # #     try:
        # #         department_id = int(self.data.get("department"))
        # #         self.fields["activity"].queryset = Activity.objects.filter(
        # #             department_id=department_id
        # #         ).order_by("name")

        #     except (ValueError, TypeError):
        #         pass  # invalid input from the client; ignore and fallback to empty Activity queryset
        # elif self.instance.pk:
        #     self.fields["activity"].queryset = (
        #         self.instance.department.activity_set.order_by("name")
        #     )

        #     except (ValueError, TypeError):
        #         self.fields["activity"].queryset = Activity.objects.none()
        # elif self.instance.pk:
        #     self.fields["activity"].queryset = self.instance.department.activity_set.order_by("name")
        # else:
        #     self.fields["activity"].queryset = Activity.objects.none()


class VolunteerRequestItemAdmin(admin.ModelAdmin):
    form = VolunteerRequestItemAdminForm

    list_display = (
        "volunteer_request",
        "get_new",
        "department",
        "get_activity",
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
        # "activity",
        "whishes",
        "reference",
        "get_volunteer_request_name",
        "get_volunteer_request_email",
        "get_volunteer_request_phone",
        "get_activity",
    )

    list_filter = (
        VolunteerRequestItemListFilter,
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

    actions = [
        "reject_request",
        "mark_not_interested",
        "accept_request",
        "fix_waiting_with_existing_person",
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
            return queryset

        return queryset.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user)
        )

    def reject_request(self, request, queryset):
        """Set status to REJECTED for selected items"""
        updated = queryset.filter(status="NEW").update(
            status="REJECTED", finished=timezone.now()
        )
        self.message_user(request, f"{updated} anmodning(er) afvist.")

    reject_request.short_description = "Afvis anmodning(er)"

    def mark_not_interested(self, request, queryset):
        """Set status to NOT_INTERESTED for selected items"""
        updated = queryset.filter(status="NEW").update(
            status="NOT_INTERESTED", finished=timezone.now()
        )
        self.message_user(
            request, f"{updated} anmodning(er) markeret som 'ikke interesseret'."
        )

    mark_not_interested.short_description = "Marker som 'ikke interesseret'"

    def accept_request(self, request, queryset):
        """Accept request - automatically handle existing person or send account creation email"""
        accepted_count = 0
        waiting_count = 0

        for obj in queryset.filter(status="NEW"):
            if obj.volunteer_request.person:
                # Person exists - create Volunteer record and set status to ACTIVE
                # Create Volunteer record only for the specific item being accepted
                # If this item is for a specific activity, create volunteer for that activity
                # If this item is for a department (without specific activity), create volunteer for department only
                if obj.activity:
                    # This is an activity-specific volunteer request
                    obj.volunteer_request.person.allow_contact_from_cpdk = (
                        obj.volunteer_request.allow_contact_from_cpdk
                    )
                    obj.volunteer_request.person.allow_contact_from_other = (
                        obj.volunteer_request.allow_contact_from_other
                    )
                    obj.volunteer_request.person.save(
                        update_fields=[
                            "allow_contact_from_cpdk",
                            "allow_contact_from_other",
                        ]
                    )
                    volunteer = Volunteer.objects.create(
                        person=obj.volunteer_request.person,
                        department=obj.activity.department,  # Use the activity's department
                        activity=obj.activity,
                        start_date=timezone.now().date(),
                        end_date=obj.activity.end_date,
                    )
                    # Try to set info fields if they exist
                    try:
                        volunteer.info_reference = obj.volunteer_request.info_reference
                        volunteer.info_whishes = obj.volunteer_request.info_whishes
                        volunteer.save()
                    except AttributeError:
                        pass  # Fields don't exist yet
                else:
                    # This is a department-level volunteer request (no specific activity)
                    obj.volunteer_request.person.allow_contact_from_cpdk = (
                        obj.volunteer_request.allow_contact_from_cpdk
                    )
                    obj.volunteer_request.person.allow_contact_from_other = (
                        obj.volunteer_request.allow_contact_from_other
                    )
                    obj.volunteer_request.person.save(
                        update_fields=[
                            "allow_contact_from_cpdk",
                            "allow_contact_from_other",
                        ]
                    )
                    volunteer = Volunteer.objects.create(
                        person=obj.volunteer_request.person,
                        department=obj.department,
                        activity=None,
                        start_date=timezone.now().date(),
                        end_date=None,
                    )
                    # Try to set info fields if they exist
                    try:
                        volunteer.info_reference = obj.volunteer_request.info_reference
                        volunteer.info_whishes = obj.volunteer_request.info_whishes
                        volunteer.save()
                    except AttributeError:
                        pass  # Fields don't exist yet

                # Update status to ACTIVE
                obj.status = "ACTIVE"
                obj.finished = timezone.now()
                obj.save()
                accepted_count += 1

                # Check if there are other items for the same request that are still NEW
                other_new_requests = VolunteerRequestItem.objects.filter(
                    volunteer_request=obj.volunteer_request, status="NEW"
                )
                if not other_new_requests.exists():
                    obj.volunteer_request.finished = timezone.now()
                    obj.volunteer_request.save()
            else:
                # Person doesn't exist - set status to WAITING and send account creation email
                obj.status = "WAITING"
                obj.save()

                # Send email with link to create user
                try:
                    self._send_account_creation_email(request, obj)
                    waiting_count += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f"Fejl ved afsendelse af email til {obj.volunteer_request.email}: {e}",
                        level="ERROR",
                    )

        # Provide feedback about what happened
        messages = []
        if accepted_count > 0:
            messages.append(
                f"{accepted_count} anmodning(er) accepteret og frivillig-poster oprettet"
            )
        if waiting_count > 0:
            messages.append(
                f"{waiting_count} anmodning(er) sat til 'venter' og emails sendt til nye brugere"
            )

        if messages:
            self.message_user(request, ". ".join(messages) + ".")

    accept_request.short_description = "Accepter anmodning"

    def fix_waiting_with_existing_person(self, request, queryset):
        """Fix WAITING volunteer request items where the person now exists"""
        fixed_count = 0
        for obj in queryset.filter(status="WAITING"):
            # Try to find existing person with matching email
            try:
                from members.models.person import Person

                person = Person.objects.get(email__iexact=obj.volunteer_request.email)

                # Link the volunteer request to the person
                obj.volunteer_request.person = person
                obj.volunteer_request.save()
                person.allow_contact_from_cpdk = (
                    obj.volunteer_request.allow_contact_from_cpdk
                )
                person.allow_contact_from_other = (
                    obj.volunteer_request.allow_contact_from_other
                )
                person.save(
                    update_fields=[
                        "allow_contact_from_cpdk",
                        "allow_contact_from_other",
                    ]
                )

                # Create volunteer record
                if obj.activity:
                    volunteer = Volunteer.objects.create(
                        person=person,
                        department=obj.activity.department,
                        activity=obj.activity,
                        start_date=timezone.now().date(),
                        end_date=obj.activity.end_date,
                    )
                else:
                    volunteer = Volunteer.objects.create(
                        person=person,
                        department=obj.department,
                        activity=None,
                        start_date=timezone.now().date(),
                        end_date=None,
                    )

                # Try to set info fields if they exist
                try:
                    volunteer.info_reference = obj.volunteer_request.info_reference
                    volunteer.info_whishes = obj.volunteer_request.info_whishes
                    volunteer.save()
                except AttributeError:
                    pass

                # Update status to ACTIVE
                obj.status = "ACTIVE"
                obj.finished = timezone.now()
                obj.save()

                fixed_count += 1

            except Person.DoesNotExist:
                continue  # Person doesn't exist yet
            except Exception as e:
                self.message_user(
                    request, f"Fejl ved behandling af {obj}: {e}", level="ERROR"
                )

        self.message_user(
            request,
            f"{fixed_count} ventende anmodning(er) rettet og frivillig-poster oprettet.",
        )

    fix_waiting_with_existing_person.short_description = (
        "Ret ventende anmodninger for eksisterende personer"
    )

    def _send_account_creation_email(self, request, volunteer_request_item):
        """Send email with account creation link"""
        # Ensure email template exists
        template = self._ensure_volunteer_account_creation_template()

        token = volunteer_request_item.volunteer_request.token
        create_user_url = request.build_absolute_uri(
            reverse("account_create_from_volunteer", args=[token])
        )

        context = {
            "name": volunteer_request_item.volunteer_request.name,
            "create_user_url": create_user_url,
            "department_name": volunteer_request_item.department.name,
            "activity_name": (
                volunteer_request_item.activity.name
                if volunteer_request_item.activity
                else None
            ),
        }

        template.makeEmail(
            [volunteer_request_item.volunteer_request.email],
            context,
            allow_multiple_emails=True,
        )

    def _ensure_volunteer_account_creation_template(self):
        """Ensure the VOLUNTEER_ACCOUNT_CREATION email template exists"""
        template_id = "VOLUNTEER_ACCOUNT_CREATION"

        try:
            template = EmailTemplate.objects.get(idname=template_id)
        except EmailTemplate.DoesNotExist:
            # Create the template if it doesn't exist
            body_html = "<h2>Opret din konto - Coding Pirates</h2>\n"
            body_html += "<p>Hej {{ name }},</p>\n"
            body_html += "\n"
            body_html += "<p>Tak for din interesse i at blive frivillig hos Coding Pirates!</p>\n"
            body_html += "\n"
            body_html += "<p>Din anmodning om at blive frivillig hos <strong>{{ department_name }}</strong>"
            body_html += "{% if activity_name %} for aktiviteten <strong>{{ activity_name }}</strong>{% endif %} "
            body_html += "er blevet godkendt.</p>\n"
            body_html += "\n"
            body_html += (
                "<p>For at fortsætte skal du oprette en konto i vores system:</p>\n"
            )
            body_html += '<p><a href="{{ create_user_url }}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Opret konto</a></p>\n'
            body_html += "\n"
            body_html += "<p>Når du har oprettet din konto, vil du automatisk blive registreret som frivillig.</p>\n"
            body_html += "\n"
            body_html += "<p>Med venlig hilsen,<br>\n"
            body_html += "Coding Pirates Danmark</p>"

            body_text = "Hej {{ name }},\n"
            body_text += "\n"
            body_text += (
                "Tak for din interesse i at blive frivillig hos Coding Pirates!\n"
            )
            body_text += "\n"
            body_text += "Din anmodning om at blive frivillig hos {{ department_name }}"
            body_text += (
                "{% if activity_name %} for aktiviteten {{ activity_name }}{% endif %} "
            )
            body_text += "er blevet godkendt.\n"
            body_text += "\n"
            body_text += "For at fortsætte skal du oprette en konto i vores system ved at følge dette link:\n"
            body_text += "{{ create_user_url }}\n"
            body_text += "\n"
            body_text += "Når du har oprettet din konto, vil du automatisk blive registreret som frivillig.\n"
            body_text += "\n"
            body_text += "Med venlig hilsen,\n"
            body_text += "Coding Pirates Danmark"

            template = EmailTemplate.objects.create(
                idname=template_id,
                name="Opret konto - Frivillig anmodning godkendt",
                description="Email til godkendte frivillige der skal oprette konto",
                subject="Opret din konto - Coding Pirates frivillig",
                from_address="kontakt@codingpirates.dk",
                body_html=body_html,
                body_text=body_text,
                template_help="Template til kontooprettelse for frivillige. Tilgængelige variable: name, create_user_url, department_name, activity_name",
            )

        return template

    class Media:
        js = ("members/js/admin.js",)

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

    def get_activity(self, obj):
        if obj.activity is None:
            return None
        else:
            return obj.activity.name

    get_activity.short_description = "Aktivitet"
