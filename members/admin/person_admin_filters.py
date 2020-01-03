from django.contrib import admin
from members.models import Department, Activity


class PersonParticipantListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "Deltager på"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "participant_list"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            my_departments = Department.objects.all()
        else:
            my_departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )

        activitys = [("none", "Deltager ikke"), ("any", "Alle deltagere samlet")]
        for activity in (
            Activity.objects.filter(department__in=my_departments)
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
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            my_departments = Department.objects.all()
        else:
            my_departments = Department.objects.filter(
                adminuserinformation__user=request.user
            )

        activitys = [("none", "Ikke inviteret til noget"), ("any", "Alle inviterede")]
        for activity in (
            Activity.objects.filter(department__in=my_departments)
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
    # Title shown in filter view
    title = "Venteliste"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "waiting_list"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            department_queryset = Department.objects.all().order_by("address__zipcode")
        else:
            department_queryset = Department.objects.filter(
                adminuserinformation__user=request.user
            ).order_by("address__zipcode")

        departments = [
            ("any", "Alle opskrevne samlet"),
            ("none", "Ikke skrevet på venteliste"),
        ]
        for department in department_queryset:
            departments.append((str(department.pk), department.name))

        return departments

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        if self.value() == "any":
            return queryset.exclude(waitinglist__isnull=True)
        elif self.value() == "none":
            return queryset.filter(waitinglist__isnull=True)
        elif self.value() is None:
            return queryset
        else:
            return queryset.filter(waitinglist__department__pk=self.value())


class VolunteerListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = "frivillig i"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "volunteer"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            department_queryset = Department.objects.all()
        else:
            department_queryset = Department.objects.filter(
                adminuserinformation__user=request.user
            )

        departments = [("any", "Alle frivillige samlet"), ("none", "Ikke frivillig")]
        for department in department_queryset:
            departments.append((str(department.pk), department.name))

        return departments

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

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
