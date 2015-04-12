from uuid import uuid4
from django.contrib import admin
from members.models import Person, Department, Volunteer, Member, Activity, ActivityInvite, ActivityParticipant,Family, EmailItem, Journal

class MemberInline(admin.TabularInline):
    model = Member
    extra = 0

class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0

class DepartmentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['name']})
    ]
    list_display = ('name','no_members')
    inlines = [MemberInline, ActivityInline]
admin.site.register(Department,DepartmentAdmin)

class MemberAdmin(admin.ModelAdmin):
    list_display = ('name','department', 'member_since','is_active')
    list_filter = ['department']
admin.site.register(Member, MemberAdmin)

class ActivityParticipantInline(admin.TabularInline):
    model = ActivityParticipant
    extra = 1

class EmailItemInline(admin.TabularInline):
    model = EmailItem
    fields = ['person','activity','subject','created_dtm','sent_dtm']
    can_delete = False
    readonly_fields = ['person','activity','subject','created_dtm','sent_dtm']
    def has_add_permission(self,request,obj=None):
        return False
    def has_delete_permission(self,request,obj=None):
        return False
    extra = 0

class ActivityInviteInline(admin.TabularInline):
    model = ActivityInvite
    extra = 3

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'start_date', 'end_date', 'is_historic')
    inlines = [ActivityParticipantInline, ActivityInviteInline, EmailItemInline]
admin.site.register(Activity, ActivityAdmin)

class PersonInline(admin.TabularInline):
    model = Person
    extra = 0

class FamilyAdmin(admin.ModelAdmin):
    list_display = ('email','unique')
    search_fields = ('email',)
    inlines = [PersonInline]
    actions = ['create_new_uuid']
    def create_new_uuid(self,request, queryset):
        for family in queryset:
            family.unique = uuid4()
            family.save()
        if queryset.count() == 1:
            message_bit = "1 familie"
        else:
            message_bit = "%s familier" % queryset.count()
        self.message_user(request, "%s fik nyt UUID." % message_bit)
    create_new_uuid.short_description = 'Opret nyt UUID'
admin.site.register(Family, FamilyAdmin)

class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'zipcode', 'streetname', 'housenumber', 'floor', 'door', 'placename', 'email', 'waiting_list_since','family_url','unique')
    inlines = [MemberInline, EmailItemInline]
    search_fields = ('name', 'zipcode')
    list_filter = ['on_waiting_list']
    def family_url(self, item):
        return '<a href="../family/%d">%s</a>' % (item.family.id, item.family.email)
    family_url.allow_tags = True
    family_url.short_description = 'Familie'
    def waiting_list_since(self,item):
        return item.on_waiting_list_since if item.on_waiting_list else None
    waiting_list_since.short_description = 'Venteliste siden'
    waiting_list_since.admin_order_field = 'on_waiting_list_since'
    def unique(self, item):
        return item.family.unique if item.family != None else ''


admin.site.register(Person,PersonAdmin)

class JournalAdmin(admin.ModelAdmin):
    readonly_fields = ['family', 'person']

admin.site.register(Journal, JournalAdmin)