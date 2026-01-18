from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

# from members.admin.admin_actions import export_participants_csv
from members.admin.admin_actions import AdminActions
from members.forms.season_fee_update_form import SeasonFeeUpdateForm
from members.models import (
    ActivityParticipant,
    Address,
    AdminUserInformation,
    Department,
    Union,
)
from members.models.activitytype import ActivityType

from .inlines import EmailItemInline


class ActivityParticipantInline(admin.TabularInline):
    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css

    model = ActivityParticipant
    extra = 0
    classes = ["hideheader"]
    fields = (
        "person",
        "note",
        "photo_permission",
        "payment_info_html",
    )
    readonly_fields = fields
    can_delete = False

    def get_queryset(self, request):
        return ActivityParticipant.objects.all().order_by("person")


class ActivityUnionListFilter(admin.SimpleListFilter):
    title = "Lokalforeninger"
    parameter_name = "department__union"

    def lookups(self, request, model_admin):
        unions = []
        for union1 in (
            Union.objects.filter(
                department__union__in=AdminUserInformation.get_unions_admin(
                    request.user
                )
            )
            .order_by("name")
            .distinct()
        ):
            unions.append((str(union1.pk), str(union1.name)))

        if len(unions) <= 1:
            return ()

        return unions

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(department__union__pk=self.value())


class ActivityTypeListFilter(admin.SimpleListFilter):
    title = "Aktivitetstype"
    parameter_name = "activitytype__id"

    def lookups(self, request, model_admin):
        activitytypes = []

        if request.user.is_superuser:
            for activitytype in ActivityType.objects.all():
                activitytypes.append(
                    (str(activitytype.pk), str(activitytype.display_name))
                )
        else:
            for activitytype in ActivityType.objects.exclude(id="FORENINGSMEDLEMSKAB"):
                activitytypes.append(
                    (str(activitytype.pk), str(activitytype.display_name))
                )

        if len(activitytypes) <= 1:
            return ()

        return activitytypes

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(activitytype_id=self.value())


class ActivityDepartmentListFilter(admin.SimpleListFilter):
    title = "Afdelinger"
    parameter_name = "department"

    def lookups(self, request, model_admin):
        departments = []
        for department1 in (
            Department.objects.filter(
                activity__department__in=AdminUserInformation.get_departments_admin(
                    request.user
                )
            )
            .order_by("name")
            .distinct()
        ):
            departments.append((str(department1.pk), str(department1)))

        if len(departments) <= 1:
            return ()

        return departments

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(department__pk=self.value())


class ActivityAdmin(admin.ModelAdmin):
    actions = [AdminActions.export_participants_csv, "update_season_fee_action"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "season_fee_update/",
                self.admin_site.admin_view(self.season_fee_update_view),
                name="season_fee_update",
            ),
        ]
        return custom_urls + urls

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove update_season_fee_action if user is not superuser or lacks permission
        if "update_season_fee_action" in actions:
            if not (
                request.user.is_superuser
                or request.user.has_perm("members.change_season_fee")
            ):
                del actions["update_season_fee_action"]
        return actions

    # --- Custom admin actions ---

    def update_season_fee_action(self, request, queryset):
        if not (
            request.user.is_superuser
            or request.user.has_perm("members.change_season_fee")
        ):
            self.message_user(
                request,
                "Du har ikke rettigheder til at opdatere sæsonbidrag.",
                level=messages.ERROR,
            )
            return
        # If no value is provided, redirect to custom form view
        if not request.POST.get("season_fee_value"):
            selected = queryset.values_list("pk", flat=True)
            ids = ",".join(str(pk) for pk in selected)
            return redirect(f"season_fee_update/?ids={ids}")
        # If value is provided, process as before
        try:
            new_fee = float(request.POST.get("season_fee_value"))
        except (TypeError, ValueError):
            self.message_user(
                request, "Ugyldig værdi for sæsonbidrag.", level=messages.ERROR
            )
            return
        updated = queryset.update(season_fee=new_fee)
        self.message_user(
            request,
            f"Opdaterede sæsonbidrag for {updated} aktiviteter.",
            level=messages.SUCCESS,
        )

    update_season_fee_action.short_description = "Opdater sæsonbidrag"
    list_per_page = settings.LIST_PER_PAGE

    def get_list_display(self, request):
        base = [
            "name",
            "activitytype",
            "start_end",
            "open_invite",
            "price_in_dkk",
            "seats_total",
            "seats_used",
            "seats_free",
            "age",
        ]
        if request.user.is_superuser:
            base += ["season_fee_short"]
        base += ["union_link", "department_link"]
        return base

    def season_fee_update_view(self, request):
        # Get selected activity IDs from query params
        ids = request.GET.get("ids", "")
        id_list = [int(pk) for pk in ids.split(",") if pk.isdigit()]
        queryset = self.model.objects.filter(pk__in=id_list)
        if not (
            request.user.is_superuser
            or request.user.has_perm("members.change_season_fee")
        ):
            self.message_user(
                request,
                "Du har ikke rettigheder til at opdatere sæsonbidrag.",
                level=messages.ERROR,
            )
            return redirect("..")
        error_message = None
        if request.method == "POST":
            form = SeasonFeeUpdateForm(request.POST)
            if form.is_valid():
                new_fee = form.cleaned_data["season_fee_value"]
                reason = form.cleaned_data["reason"]
                # Validation: no negative, not above price_in_dkk
                if new_fee < 0:
                    error_message = "Sæsonbidrag kan ikke være negativt."
                else:
                    over_price = [
                        a for a in queryset if new_fee > (a.price_in_dkk or 0)
                    ]
                    if over_price:
                        error_message = "Sæsonbidrag kan ikke være højere end prisen for en eller flere aktiviteter."
                if not error_message:
                    updated = 0
                    for activity in queryset:
                        activity.season_fee = new_fee
                        activity.season_fee_change_reason = reason
                        activity.save(
                            update_fields=["season_fee", "season_fee_change_reason"]
                        )
                        # Log the change in admin history
                        self.log_change(
                            request,
                            activity,
                            f"[Bulk] Sæsonbidrag ændret til {new_fee} (Begrundelse: {reason}) via admin handling.",
                        )
                        updated += 1
                    self.message_user(
                        request,
                        f"Opdaterede sæsonbidrag for {updated} aktiviteter.",
                        level=messages.SUCCESS,
                    )
                    return redirect("..")
        else:
            form = SeasonFeeUpdateForm()
        return render(
            request,
            "admin/season_fee_update_form.html",
            {"form": form, "activities": queryset, "error_message": error_message},
        )

    date_hierarchy = "start_date"
    search_fields = (
        "name",
        "department__union__name",
        "department__name",
        "description",
    )

    def get_readonly_fields(self, request, obj=None):
        base = [
            "seats_left",
            "participants",
            "activity_link",
            "addressregion",
        ]
        # Only allow users with 'members.change_season_fee' to edit the field and reason
        if not (
            request.user.is_superuser
            or request.user.has_perm("members.change_season_fee")
        ):
            base.append("season_fee")
            base.append("season_fee_change_reason")
        return base

    def save_model(self, request, obj, form, change):
        # Only set season_fee to default if no override reason is given
        if not obj.season_fee_change_reason:
            if obj.activitytype_id == "FORLØB":
                obj.season_fee = 150
            else:
                obj.season_fee = 0
        # else: keep the user-set value (with reason)
        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not (
            request.user.is_superuser
            or request.user.has_perm("members.change_season_fee")
        ):
            new_fieldsets = []
            for name, opts in fieldsets:
                fields = list(opts.get("fields", ()))
                if "season_fee_change_reason" in fields:
                    fields.remove("season_fee_change_reason")
                opts = dict(opts)
                opts["fields"] = tuple(fields)
                new_fieldsets.append((name, opts))
            return new_fieldsets
        return fieldsets

    raw_id_fields = (
        "union",
        "department",
    )
    list_filter = (
        ActivityUnionListFilter,
        ActivityDepartmentListFilter,
        "open_invite",
        ActivityTypeListFilter,
        "address__region",
    )
    autocomplete_fields = (
        "address",
        "department",
    )
    save_as = True

    ordering = ("-start_date", "department__name", "name")

    class Media:
        css = {"all": ("members/css/custom_admin.css",)}  # Include extra css
        js = ("members/js/copy_to_clipboard.js",)

    inlines = [ActivityParticipantInline, EmailItemInline]

    def start_end(self, obj):
        return str(obj.start_date) + " - " + str(obj.end_date)

    start_end.short_description = "Periode"
    start_end.admin_order_field = "start_date"

    def age(self, obj):
        return str(obj.min_age) + " - " + str(obj.max_age)

    age.short_description = "Alder"
    age.admin_order_field = "min_age"

    def union_link(self, item):
        url = reverse("admin:members_union_change", args=[item.department.union_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.department.union.name))
        return mark_safe(link)

    union_link.short_description = "Forening"
    union_link.admin_order_field = "department__union__name"

    def department_link(self, item):
        url = reverse("admin:members_department_change", args=[item.department_id])
        link = '<a href="%s">%s</a>' % (url, escape(item.department.name))
        return mark_safe(link)

    department_link.short_description = "Afdeling"
    department_link.admin_order_field = "department__name"

    def seats_total(self, obj):
        return str(obj.max_participants)

    seats_total.short_description = "Total"
    seats_total.admin_order_field = "max_participants"

    def seats_used(self, obj):
        return str(obj.activityparticipant_set.count())

    seats_used.short_description = "Besat"

    def seats_free(self, obj):
        return str(obj.max_participants - obj.activityparticipant_set.count())

    seats_free.short_description = "Ubesat"

    def addressregion(self, obj):
        return str(obj.address.region)

    def season_fee_short(self, obj):
        return f"{obj.season_fee}"

    season_fee_short.short_description = "Sæsonbidrag"

    addressregion.short_description = "Region"

    def activity_membership_union_link(self, obj):
        if obj.activitytype_id in ["FORENINGSMEDLEMSKAB", "STØTTEMEDLEMSKAB"]:
            url = reverse("admin:members_union_change", args=[obj.union_id])
            link = '<a href="%s">%s</a>' % (url, escape(obj.union.name))
            return mark_safe(link)
        else:
            return ""

    activity_membership_union_link.short_description = "Forening for medlemskab"

    def activity_link(self, obj):
        if obj.id is None:
            return ""

        full_url = (
            f"{settings.BASE_URL}{reverse('activity_view_family', args=[obj.id])}"
        )
        link = format_html(
            '<a href="{}" target="_blank">{}</a> '
            '<button type="button" class="copy-btn" data-url="{}">Copy to clipboard</button>',
            full_url,
            full_url,
            full_url,
        )

        return mark_safe(link)

    activity_link.short_description = "Link til aktivitet"

    # Only view activities on own department
    def get_queryset(self, request):
        qs = super(ActivityAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "members.view_all_departments"
        ):
            return qs
        departments = Department.objects.filter(adminuserinformation__user=request.user)
        return qs.filter(department__in=departments).exclude(
            activitytype_id="FORENINGSMEDLEMSKAB"
        )

    # Solution found on https://stackoverflow.com/questions/57056994/django-model-form-with-only-view-permission-puts-all-fields-on-exclude
    # formfield_for_foreignkey described in documentation here: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.formfield_for_foreignkey
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Only show own departments when creating new activity
        if db_field.name == "department":
            departments = Department.objects.filter(
                models.Q(closed_dtm__isnull=True)
                | models.Q(closed_dtm__gt=timezone.now().date())
            )
            # If editing an existing activity, include its department even if closed
            obj = getattr(request, "activity_obj", None)
            if (
                not obj
                and hasattr(request, "resolver_match")
                and request.resolver_match
            ):
                # Try to get the object from the URL if possible
                try:
                    from members.models.activity import Activity

                    pk = request.resolver_match.kwargs.get("object_id")
                    if pk:
                        obj = Activity.objects.filter(pk=pk).first()
                except Exception:
                    obj = None

            if obj and obj.department_id:
                departments = Department.objects.filter(
                    models.Q(pk=obj.department_id)
                    | models.Q(closed_dtm__isnull=True)
                    | models.Q(closed_dtm__gt=timezone.now().date())
                )

            if request.user.is_superuser or request.user.has_perm(
                "members.view_all_departments"
            ):
                kwargs["queryset"] = departments
            else:
                kwargs["queryset"] = departments.filter(
                    adminuserinformation__user=request.user
                )

        if db_field.name == "address":
            kwargs["queryset"] = Address.get_user_addresses(request.user)

        if db_field.name == "activitytype" and not request.user.is_superuser:
            kwargs["queryset"] = ActivityType.objects.exclude(id="FORENINGSMEDLEMSKAB")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def delete_queryset(self, request, queryset):
        for activity in queryset:
            print(activity)
            self.delete_model(request, activity)

    def delete_model(self, request, activity):
        try:
            activity.delete()
            messages.success(request, f'Aktivitet "{activity.name}" slettet.')
        except ValidationError as e:
            messages.error(request, e.message)

        except Exception as e:
            messages.error(request, f"Fejl: {str(e)}")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Only set initial for new objects (not editing existing)
        if obj is None:
            departments = Department.objects.filter(
                models.Q(closed_dtm__isnull=True)
                | models.Q(closed_dtm__gt=timezone.now().date())
            )
            if not (
                request.user.is_superuser
                or request.user.has_perm("members.view_all_departments")
            ):
                departments = departments.filter(
                    adminuserinformation__user=request.user
                )
            if departments.count() == 1:
                form.base_fields["department"].initial = departments.first().pk
        return form

    fieldsets = [
        (
            "Afdeling",
            {
                "description": "<p>Du kan ændre afdeling for aktiviteten ved at vælge en afdeling i listen, evt bruge søgefunktionen.</p>",
                "fields": ("department",),
            },
        ),
        (
            "Aktivitet",
            {
                "description": """<p>Aktivitetsnavnet skal afspejle aktivitet samt tidspunkt.
                F.eks. <em>Forårssæsonen 2026</em>.</p>
                <p>Tidspunkt er f.eks. <em>Onsdage 17:00-19:00</em></p>
                <p>Startdato er første dag for aktiviteten, og slutdato er sidste for aktiviteten</p>""",
                "fields": (
                    "name",
                    "activitytype",
                    "season_fee",
                    "season_fee_change_reason",
                    "activity_link",
                    "open_hours",
                    "description",
                    (
                        "start_date",
                        "end_date",
                    ),
                    "visible",
                    "visible_from",
                ),
            },
        ),
        (
            "Lokation og ansvarlig",
            {
                "description": """<p>Adresse samt ansvarlig kan adskille sig fra afdelingens
                informationer (f.eks. et gamejam der kan foregå et andet sted).</p>""",
                "fields": (
                    "address",
                    "addressregion",
                    "responsible_name",
                    "responsible_contact",
                ),
            },
        ),
        (
            "Tilmeldingsdetaljer",
            {
                "description": """<p>Tilmeldingsinstruktioner er tekst der kommer til at stå på
                betalingsformularen på tilmeldingssiden.</p>
                <p>Den skal bruges til at stille spørgsmål, som den, der tilmelder sig,
                kan besvare ved tilmelding.</p>
                <p>Fri tilmelding betyder, at alle, når som helst kan tilmelde sig denne
                aktivitet - efter "først til mølle"-princippet.
                Dette er kun til aktiviteter og klubaften-forløb/sæsoner i områder,
                hvor der ikke er nogen venteliste. </p>
                <p>Alle aktiviteter med fri tilmelding kommer til at stå med en stor "tilmeld"
                knap på medlemssiden. <b>Afdelinger med venteliste bruger typisk ikke fri
                tilmelding - spørg i Slack hvis du er i tvivl!</b></p>""",
                "fields": (
                    "instructions",
                    (
                        "signup_closing",
                        "open_invite",
                    ),
                    "price_in_dkk",
                    (
                        "max_participants",
                        "participants",
                        "seats_left",
                    ),
                    (
                        "min_age",
                        "max_age",
                    ),
                ),
            },
        ),
    ]
