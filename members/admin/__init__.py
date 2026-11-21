# Ensure ActivityMode admin registration is loaded
from .activitymode_admin import ActivityModeAdmin  # noqa: F401
from django.contrib import admin

from django.contrib.auth.models import User

from members.models import (
    Activity,
    ActivityInvite,
    ActivityParticipant,
    Address,
    AnonymizationCandidate,
    Consent,
    Department,
    EmailTemplate,
    Equipment,
    Family,
    Member,
    Municipality,
    Payment,
    Person,
    Union,
    WaitingList,
    EmailItem,
    Volunteer,
    VolunteerRequest,
    VolunteerRequestItem,
    SlackInviteLog,
    SlackInvitationSetup,
    AuthLog,
)

from .activity_admin import ActivityAdmin
from .activityinvite_admin import ActivityInviteAdmin
from .activityparticipant_admin import ActivityParticipantAdmin
from .address_admin import AddressAdmin
from .anonymization_candidates_admin import AnonymizationCandidatesAdmin
from .consent_admin import ConsentAdmin
from .department_admin import DepartmentAdmin
from .equipment_admin import EquipmentAdmin
from .family_admin import FamilyAdmin
from .member_admin import MemberAdmin
from .municipality_admin import MunicipalityAdmin
from .payment_admin import PaymentAdmin
from .person_admin import PersonAdmin
from .union_admin import UnionAdmin
from .user_admin import UserAdmin
from .waitinglist_admin import WaitingListAdmin
from .emailitem_admin import EmailItemAdmin
from .volunteer_admin import VolunteerAdmin
from .volunteerrequest_admin import VolunteerRequestAdmin
from .volunteerrequestitem_admin import VolunteerRequestItemAdmin
from .notifications import get_admin_notifications
from .slackinvitelog_admin import SlackInviteLogAdmin
from .authlog_admin import AuthLogAdmin
from .slackinvitesetup_admin import SlackInvitationSetupAdmin


default_each_context = admin.site.each_context


def members_admin_each_context(request):
    context = default_each_context(request)
    context["admin_notifications"] = get_admin_notifications(request)
    return context


admin.site.each_context = members_admin_each_context

_original_get_app_list = admin.site.get_app_list


def members_get_app_list(request, app_label=None):
    """Show the login log under 'Godkendelse og autorisation' in the menu"""
    app_list = _original_get_app_list(request, app_label)
    auth_log_models = []
    for app in app_list:
        if app["app_label"] == "members":
            auth_log_models = [
                m for m in app["models"] if m["object_name"] == "AuthLog"
            ]
            app["models"] = [m for m in app["models"] if m not in auth_log_models]
    if not auth_log_models:
        return app_list
    auth_app = next((a for a in app_list if a["app_label"] == "auth"), None)
    if auth_app is not None:
        auth_app["models"].extend(auth_log_models)
    return [a for a in app_list if a["models"]]


admin.site.get_app_list = members_get_app_list

admin.site.site_header = "Coding Pirates Medlemsdatabase"
admin.site.index_title = "Afdelings admin"

admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityInvite, ActivityInviteAdmin)
admin.site.register(ActivityParticipant, ActivityParticipantAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(AnonymizationCandidate, AnonymizationCandidatesAdmin)
admin.site.register(Consent, ConsentAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(EmailTemplate)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Municipality, MunicipalityAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Union, UnionAdmin)
admin.site.register(WaitingList, WaitingListAdmin)
admin.site.register(EmailItem, EmailItemAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(VolunteerRequest, VolunteerRequestAdmin)
admin.site.register(VolunteerRequestItem, VolunteerRequestItemAdmin)
admin.site.register(SlackInviteLog, SlackInviteLogAdmin)
admin.site.register(AuthLog, AuthLogAdmin)
admin.site.register(SlackInvitationSetup, SlackInvitationSetupAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# admin.site.register(AdminUserInformation, AdminUserInformationAdmin)
