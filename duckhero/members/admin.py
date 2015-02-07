from django.contrib import admin
from members.models import Person, Department, Volunteer, Member, Activity, ActivityInvite, WaitingList, ActivityParticipant
# Register your models here.
admin.site.register(Person)
admin.site.register(WaitingList)

class MemberInline(admin.TabularInline):
    model = Member
    extra = 1
class DepartmentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['name']})
    ]
    list_display = ('name','no_members')
    inlines = [MemberInline]
admin.site.register(Department,DepartmentAdmin)

class MemberAdmin(admin.ModelAdmin):
    list_display = ('name','department', 'is_active')
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
