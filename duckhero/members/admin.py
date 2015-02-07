from django.contrib import admin
from members.models import Person, Department, Volunteer, Member, Activity, ActivityInvite, WaitingList, ActivityParticipant
# Register your models here.


class MemberInline(admin.TabularInline):
    model = Member
    extra = 0
class DepartmentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['name']})
    ]
    list_display = ('name','no_members')
    inlines = [MemberInline]
admin.site.register(Department,DepartmentAdmin)

class MemberAdmin(admin.ModelAdmin):
    list_display = ('name','department', 'member_since','is_active')
    list_filter = ['department']
admin.site.register(Member, MemberAdmin)

class ActivityParticipantInline(admin.TabularInline):
    model = ActivityParticipant
    extra = 1

class ActivityInviteInline(admin.TabularInline):
    model = ActivityInvite
    extra = 1

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'start', 'end', 'is_historic')
    inlines = [ActivityParticipantInline, ActivityInviteInline]
admin.site.register(Activity, ActivityAdmin)

class WaitingListInline(admin.TabularInline):
    model = WaitingList
    extra = 0

class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'street', 'placename','zipcity', 'email')
    inlines = [MemberInline,WaitingListInline]
    search_fields = ('name', 'zipcity')
admin.site.register(Person,PersonAdmin)

class WaitingListAdmin(admin.ModelAdmin):
    list_display = ('person','department','added')
    list_filter = ['department']
admin.site.register(WaitingList,WaitingListAdmin)
