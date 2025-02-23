from django.contrib import admin
from django.utils import timezone

from members.models import Activity, AdminUserInformation
from members.models.municipality import Municipality


class PersonParticipantCurrentYearListFilter(admin.SimpleListFilter):
    title = "Deltager på (år " + str(timezone.now().year) + ")"
    parameter_name = "participant_list_current_year"

    def lookups(self, request, _model_admin):
        return [
            (str(a.pk), str(a))
            for a in Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user),
                activitytype__id__in=["FORLØB", "ARRANGEMENT"],
                start_date__year=timezone.now().year,
            ).order_by("department__name", "-start_date")
        ]

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(activityparticipant__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(activityparticipant__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(activityparticipant__activity=self.value())


class PersonParticipantLastYearListFilter(admin.SimpleListFilter):
    title = "Deltager på (år " + str(timezone.now().year - 1) + ")"
    parameter_name = "participant_list_last_year"

    def lookups(self, request, _model_admin):
        return [
            (str(a.pk), str(a))
            for a in Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user),
                activitytype__id__in=["FORLØB", "ARRANGEMENT"],
                start_date__year=timezone.now().year - 1,
            ).order_by("department__name", "-start_date")
        ]

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(activityparticipant__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(activityparticipant__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(activityparticipant__activity=self.value())


class PersonParticipantActiveListFilter(admin.SimpleListFilter):
    title = "Deltager på (aktive)"
    parameter_name = "participant_list_active"

    def lookups(self, request, _model_admin):
        return [
            (str(a.pk), str(a))
            for a in Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user),
                activitytype__id__in=["FORLØB", "ARRANGEMENT"],
                end_date__gte=timezone.now(),
            ).order_by("department__name", "-start_date")
        ]

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(activityparticipant__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(activityparticipant__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(activityparticipant__activity=self.value())


class PersonParticipantListFilter(admin.SimpleListFilter):
    title = "Deltager på"
    parameter_name = "participant_list"

    def lookups(self, request, model_admin):
        activitys = [("none", "Deltager ikke"), ("any", "Alle deltagere samlet")]
        for activity in Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user)
        ).order_by("department__name", "-start_date"):
            activitys.append((str(activity.pk), str(activity)))

        return activitys

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(activityparticipant__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(activityparticipant__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(activityparticipant__activity=self.value())


class PersonInvitedListFilter(admin.SimpleListFilter):
    title = "Inviteret til"
    parameter_name = "activity_invited_list"

    def lookups(self, request, model_admin):
        activitys = [("none", "Ikke inviteret til noget"), ("any", "Alle inviterede")]
        for activity in Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user)
        ).order_by("department__name", "-start_date"):
            activitys.append((str(activity.pk), str(activity)))

        return activitys

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(activityinvite__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(activityinvite__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(activityinvite__activity=self.value())


class PersonWaitinglistListFilter(admin.SimpleListFilter):
    title = "Venteliste"
    parameter_name = "waiting_list"

    def lookups(self, request, model_admin):
        departments = [
            ("any", "Alle opskrevne samlet"),
            ("none", "Ikke skrevet på venteliste"),
        ]
        for department in AdminUserInformation.get_departments_admin(
            request.user
        ).order_by("name"):
            if (
                department.closed_dtm is None
                and department.union.closed_at is None
                and department.has_waiting_list is True
                and department.waitinglist_count() > 0
            ):
                departments.append((str(department.pk), department.name))

        return departments

    def queryset(self, request, queryset):
        if self.value() == "any":
            return queryset.exclude(waitinglist__isnull=True)
        elif self.value() == "none":
            return queryset.filter(waitinglist__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(waitinglist__department__pk=self.value())


class VolunteerListFilter(admin.SimpleListFilter):
    title = "Frivillig i"
    parameter_name = "volunteer"

    def lookups(self, request, model_admin):
        departments = [("any", "Alle frivillige samlet"), ("none", "Ikke frivillig")]
        for department in AdminUserInformation.get_departments_admin(
            request.user
        ).order_by("name"):
            departments.append((str(department.pk), department.name))

        return departments

    def queryset(self, request, queryset):
        if self.value() == "any":
            return (
                queryset.filter(volunteer__isnull=False)
                .filter(volunteer__removed__isnull=True)
                .distinct()
            )
        elif self.value() == "none":
            return (
                queryset.filter(volunteer__isnull=True).distinct()
                | queryset.exclude(volunteer__removed__isnull=True).distinct()
            )
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(
                volunteer__department__pk=self.value(), volunteer__removed__isnull=True
            )


class MunicipalityFilter(admin.SimpleListFilter):
    title = "Kommune"
    parameter_name = "municipality"

    def lookups(self, request, model_admin):
        municipalities = [("none", "Ingen kommune")]
        for municipality in Municipality.objects.all().order_by("name"):
            municipalities.append((str(municipality.pk), municipality.name))

        return municipalities

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(municipality__isnull=True).distinct()
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(municipality_id=self.value())


class AnonymizedFilter(admin.SimpleListFilter):
    title = "Anonymiseret"
    parameter_name = "anonymized"

    def lookups(self, request, model_admin):
        return [("yes", "Anonymiseret"), ("no", "Ikke anonymiseret")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(anonymized=True)
        elif self.value() == "no":
            return queryset.filter(anonymized=False)
        else:
            return queryset
