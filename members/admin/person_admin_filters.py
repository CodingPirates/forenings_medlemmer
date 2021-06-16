from django.contrib import admin
from members.models import Activity, AdminUserInformation
from datetime import datetime, timedelta


class PersonParticipantListFilter(admin.SimpleListFilter):
    title = "Deltager på"
    parameter_name = "participant_list"
    limitdays = None

    def lookups(self, request, model_admin):
        activitys = []
        activityList = Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user)
        ).order_by("department__name", "-start_date")

        if self.limitdays is not None:  # Limit the number of shown activities by date
            activityList = activityList.filter(
                end_date__gte=datetime.now() - timedelta(days=self.limitdays)
            )
        else:  # Only add none and any if not limited
            activitys += [("none", "Deltager ikke"), ("any", "Alle deltagere samlet")]

        for activity in activityList:
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


class PersonParticipantListFilterLimited(PersonParticipantListFilter):
    title = "Deltager på (seneste års aktiviteter)"
    limitdays = 365  # number of days


class PersonInvitedListFilter(admin.SimpleListFilter):
    title = "Inviteret til"
    parameter_name = "activity_invited_list"
    limitdays = None

    def lookups(self, request, model_admin):
        activitys = []
        activityList = Activity.objects.filter(
            department__in=AdminUserInformation.get_departments_admin(request.user)
        ).order_by("department__name", "-start_date")

        if self.limitdays is not None:  # Limit the number of shown activities by date
            activityList = activityList.filter(
                end_date__gte=datetime.now() - timedelta(days=self.limitdays)
            )
        else:  # Only add none and any if not limited
            activitys += [
                ("none", "Ikke inviteret til noget"),
                ("any", "Alle inviterede"),
            ]

        for activity in activityList:
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


class PersonInvitedListFilterLimited(PersonInvitedListFilter):
    title = "Inviteret til (seneste års aktiviteter)"
    limitdays = 365  # number of days


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
