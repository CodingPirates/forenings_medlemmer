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
    SlackInviteLog,
    SlackInvitationSetup,
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
from .slackinvitelog_admin import SlackInviteLogAdmin
from .slackinvitesetup_admin import SlackInvitationSetupAdmin

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
admin.site.register(SlackInviteLog, SlackInviteLogAdmin)
admin.site.register(SlackInvitationSetup, SlackInvitationSetupAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# admin.site.register(AdminUserInformation, AdminUserInformationAdmin)
