from uuid import uuid4
from django.contrib import admin
from members.models import Person, Department, Volunteer, Member, Activity, ActivityInvite, ActivityParticipant,Family, EmailItem, Journal, WaitingList, EmailTemplate

class MemberInline(admin.TabularInline):
    model = Member
    extra = 0

class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0

class WaitingListInline(admin.TabularInline):
    model = WaitingList
    extra = 0

class EmailItemInline(admin.TabularInline):
    model = EmailItem
    fields = ['person', 'family', 'activity','subject','created_dtm','sent_dtm']
    can_delete = False
    readonly_fields = ['person','activity','subject','created_dtm','sent_dtm']
    def has_add_permission(self,request,obj=None):
        return False
    def has_delete_permission(self,request,obj=None):
        return False
    extra = 0

class DepartmentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['name', 'description', 'open_hours', 'responsible_name', 'responsible_contact', 'placename', 'streetname', 'housenumber', 'floor', 'door', 'city', 'zipcode', 'has_waiting_list']})
    ]
    list_display = ('name','no_members')
    inlines = [MemberInline, ActivityInline,WaitingListInline, EmailItemInline]
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
    extra = 3

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'start_date', 'end_date', 'is_historic')
    date_hierarchy = 'start_date'
    inlines = [ActivityParticipantInline, ActivityInviteInline, EmailItemInline]
admin.site.register(Activity, ActivityAdmin)

class PersonInline(admin.TabularInline):
    model = Person
    extra = 0

class FamilyAdmin(admin.ModelAdmin):
    list_display = ('email','unique')
    search_fields = ('email',)
    inlines = [PersonInline, EmailItemInline]
    actions = ['create_new_uuid']
    view_on_site = True
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

class PersonWaitinglistListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = 'Venteliste'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'waiting_list'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        departments = []
        for department in Department.objects.filter(has_waiting_list=True).order_by('zipcode'):
            departments.append(( str(department.pk), department.name))

        return departments

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        if(self.value() == None):
            return queryset
        else:
            return queryset.filter(waitinglist__department__pk=self.value())


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'membertype', 'family_url', 'age_years', 'zipcode', 'email', 'added')
    list_filter = ('membertype', 'gender', PersonWaitinglistListFilter)
    inlines = [MemberInline, EmailItemInline]
    search_fields = ('name', 'streetname', 'email', 'phone')
    fieldsets = (
        ('Informationer' , {
            'fields' : ('membertype', 'birthday', 'has_certificate', 'added', 'photo_permission'),
        }),
        ('Kontakt Oplysninger', {
            'fields' : ('name', 'streetname', 'housenumber', 'floor', 'door', 'city', 'zipcode', 'placename', 'email', 'phone')
        }))
    def family_url(self, item):
        return '<a href="../family/%d">%s</a>' % (item.family.id, item.family.email)
    family_url.allow_tags = True
    family_url.short_description = 'Familie'

    def unique(self, item):
        return item.family.unique if item.family != None else ''


admin.site.register(Person,PersonAdmin)

class JournalAdmin(admin.ModelAdmin):
    readonly_fields = ['family', 'person']

admin.site.register(Journal, JournalAdmin)

admin.site.register(EmailTemplate)
