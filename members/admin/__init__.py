from django.contrib import admin

from django.contrib.auth.models import User

from members.models import (
    Activity,
    ActivityInvite,
    ActivityParticipant,
    Address,
    Department,
    EmailTemplate,
    Equipment,
    Family,
    Member,
    Payment,
    Person,
    Union,
)

from .activity_admin import ActivityAdmin
from .activityinvite_admin import ActivityInviteAdmin
from .activityparticipant_admin import ActivityParticipantAdmin
from .address_admin import AddressAdmin
from .department_admin import DepartmentAdmin
from .equipment_admin import EquipmentAdmin
from .family_admin import FamilyAdmin
from .member_admin import MemberAdmin
from .payment_admin import PaymentAdmin
from .person_admin import PersonAdmin
from .union_admin import UnionAdmin
from .user_admin import UserAdmin

admin.site.site_header = "Coding Pirates Medlemsdatabase"
admin.site.index_title = "Afdelings admin"

admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityInvite, ActivityInviteAdmin)
admin.site.register(ActivityParticipant, ActivityParticipantAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(EmailTemplate)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Union, UnionAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# admin.site.register(AdminUserInformation, AdminUserInformationAdmin)
