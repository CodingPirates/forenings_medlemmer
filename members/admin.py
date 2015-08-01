from uuid import uuid4
from django.contrib import admin
from members.models import Person, Department, Volunteer, Member, Activity, ActivityInvite, ActivityParticipant,Family, EmailItem, Journal, WaitingList, EmailTemplate, AdminUserInformation, QuickpayTransaction, Payment
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse

class MemberInline(admin.TabularInline):
    model = Member
    fields = ('member_since', 'person')
    readonly_fields = fields
    extra = 0

class ActivityInline(admin.TabularInline):
    model = Activity
    fields = ('name', 'start_date', 'end_date')
    readonly_fields = fields
    extra = 0

class WaitingListInline(admin.StackedInline):
    model = WaitingList
    extra = 0

class EmailItemInline(admin.TabularInline):
    model = EmailItem
    fields = ['reciever', 'subject', 'sent_dtm']
    can_delete = False
    readonly_fields = fields
    def has_add_permission(self,request,obj=None):
        return False
    def has_delete_permission(self,request,obj=None):
        return False
    extra = 0

class DepartmentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['name', 'description', 'open_hours', 'responsible_name', 'responsible_contact', 'streetname', 'housenumber', 'floor', 'door', 'zipcode', 'city', 'placename', 'has_waiting_list']})
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
    extra = 0

class ActivityInviteInline(admin.TabularInline):
    model = ActivityInvite
    extra = 0

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'start_date', 'open_invite', 'price', 'max_participants')
    date_hierarchy = 'start_date'
    list_filter = ('department','open_invite')

    fieldsets = (
        ('Afdeling', {'fields': (
            'department',
        )
        }
         ),
        ('Aktivitet', {'fields': (
            'name',
            'open_hours',
            'description',
            'instructions',
            'open_invite',
            'price',
            'start_date',
            'end_date',
            'signup_closing',
            'max_participants',
            'min_age',
            'max_age',
            'responsible_name',
            'responsible_contact',

        )
        }
         ),
        ('Lokation', {'fields': (
            'streetname',
            'housenumber',
            'floor',
            'door',
            'zipcode',
            'city',
            'placename'
        )
        }
         )
    )


    inlines = [ActivityParticipantInline, ActivityInviteInline]
admin.site.register(Activity, ActivityAdmin)

class PersonInline(admin.TabularInline):
    model = Person
    fields = ('membertype', 'name', 'zipcode', 'added')
    readonly_fields = fields
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    fields = ('added', 'payment_type', 'confirmed_dtm', 'rejected_dtm', 'amount_ore')
    readonly_fields = ('family',)
    extra = 0

class FamilyAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        if(request.user.has_perm('members.view_family_unique')):
            return ('email', 'unique')
        else:
            return ('email',)
    search_fields = ('email',)
    inlines = [PersonInline, PaymentInline, EmailItemInline]
    actions = ['create_new_uuid', 'resend_link_email']

    fields = ('email', 'confirmed_dtm')
    readonly_fields = ('confirmed_dtm',)

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

    def resend_link_email(self,request, queryset):
        for family in queryset:
            family.send_link_email()
        if queryset.count() == 1:
            message_bit = "1 familie"
        else:
            message_bit = "%s familier" % queryset.count()
        self.message_user(request, "%s fik fik tilsendt link e-mail." % message_bit)
    resend_link_email.short_description = "Gensend link e-mail"

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
    list_display = ('name', 'membertype', 'family_url', 'age_years', 'zipcode', 'added')
    list_filter = ('membertype', 'gender', PersonWaitinglistListFilter)
    search_fields = ('name',)
    actions = ['invite_to_own_activity', 'export_emaillist']

    # needs 'view_full_address' to seet personal details.
    # email and phonenumber only shown on adults.
    def get_fieldsets(self, request, person=None):
        if(request.user.has_perm('members.view_full_address')):
            contact_fields = ('name', 'streetname', 'housenumber', 'floor', 'door', 'city', 'zipcode', 'placename', 'email', 'phone')
        else:
            if(person.membertype == Person.CHILD):
                contact_fields = ('name', 'city', 'zipcode')
            else:
                contact_fields = ('name', 'city', 'zipcode', 'email', 'phone')

        fieldsets = (
            ('Informationer' , {
                'fields' : ('membertype', 'birthday', 'has_certificate', 'added', 'family'),
            }),
            ('Kontakt Oplysninger', {
                'fields' : contact_fields
            }))

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        if type(obj) == Person and not request.user.is_superuser:
            return tuple(obj._meta.get_all_field_names())
        else:
            return []

    def family_url(self, item):
        return '<a href="../family/%d">%s</a>' % (item.family.id, item.family.email)
    family_url.allow_tags = True
    family_url.short_description = 'Familie'

    def unique(self, item):
        return item.family.unique if item.family != None else ''

    def invite_to_own_activity(self,request, queryset):
        return HttpResponse("Ikke klar endnu")
    invite_to_own_activity.short_description = "Inviter valgte personer til en aktivitet"

    def export_emaillist(self,request, queryset):
        result_string = "kopier denne liste direkte ind i dit email program (Hush at bruge Bcc!)\n\n"
        family_email = []
        for person in queryset:
            family_email.append(person.family.email)
        result_string = result_string + ',\n'.join(list(set(family_email)))

        return HttpResponse(result_string, content_type="text/plain")
    export_emaillist.short_description = "Exporter en liste af familie e-mail adresser fra de valgte personer"

admin.site.register(Person,PersonAdmin)

class JournalAdmin(admin.ModelAdmin):
    readonly_fields = ['family', 'person']

admin.site.register(Journal, JournalAdmin)

admin.site.register(EmailTemplate)

class AdminUserInformationInline(admin.StackedInline):
    model = AdminUserInformation
    can_delete = False

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (AdminUserInformationInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['added', 'payment_type', 'family', 'confirmed_dtm', 'rejected_dtm', 'activityparticipant']
    list_filter = ['payment_type', 'activity']
    date_hierarchy = 'added'
    search_fields = ('family__email',)

admin.site.register(Payment, PaymentAdmin)
admin.site.register(QuickpayTransaction)
