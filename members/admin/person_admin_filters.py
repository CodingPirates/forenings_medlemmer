from django.contrib import admin
from members.models import Department, Activity

from members.models import AdminUserInformation


class PersonParticipantListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Deltager på"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "participant_list"

    def lookups(self, request, model_admin):
        activitys = [("none", "Deltager ikke"), ("any", "Alle deltagere samlet")]
        for activity in (
            Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user)
            )
            .order_by("start_date")
            .order_by("zipcode")
        ):
            activitys.append((str(activity.pk), str(activity)))

        return activitys

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(member__activityparticipant__isnull=True)
        elif self.value() == "any":
            return queryset.exclude(member__activityparticipant__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(member__activityparticipant__activity=self.value())


class PersonInvitedListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Inviteret til"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "activity_invited_list"

    def lookups(self, request, model_admin):
        activitys = [("none", "Ikke inviteret til noget"), ("any", "Alle inviterede")]
        for activity in (
            Activity.objects.filter(
                department__in=AdminUserInformation.get_departments_admin(request.user)
            )
            .order_by("start_date")
            .order_by("zipcode")
        ):
            activitys.append((str(activity.pk), str(activity)))

        return activitys

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

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
        for department in AdminUserInformation.get_departments_admin(request.user):
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
    title = "frivillig i"
    parameter_name = "volunteer"

    def lookups(self, request, model_admin):
        departments = [("any", "Alle frivillige samlet"), ("none", "Ikke frivillig")]
        for department in AdminUserInformation.get_departments_admin(request.user):
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
