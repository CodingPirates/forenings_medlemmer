from uuid import uuid4
from django import forms
from django.contrib import admin
from members.models import Person, Department, Volunteer, Member, Activity, ActivityInvite, ActivityParticipant,Family, EmailItem, WaitingList, EmailTemplate, AdminUserInformation, QuickpayTransaction, Payment
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.core.urlresolvers import reverse
from django.utils.html import format_html

admin.site.site_header="Coding Pirates Medlemsdatabase"
admin.site.index_title="Site Admin"

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
        ('Beskrivelse',
            {'fields':('name', 'description', 'open_hours'),
            'description': '<p>Lav en beskrivelse af jeres aktiviteter, teknologier og tekniske niveau.</p><p>Åbningstid er ugedag samt tidspunkt<p>'}),
        ('Ansvarlig',
            {'fields':('responsible_name', 'responsible_contact')}),
        ('Adresse',
            {'fields':('streetname', 'housenumber', 'floor', 'door', 'zipcode', 'city', 'placename')}),
        ('Yderlige data',
            {'fields':('has_waiting_list', 'created', 'closed_dtm'),
            'description' : '<p>Venteliste betyder at børn har mulighed for at skrive sig på ventelisten (tilkendegive interesse for denne afdeling). Den skal typisk altid være krydset af.</p>',
            'classes': ('collapse',)}),
    ]

    list_display = ('name', )
admin.site.register(Department,DepartmentAdmin)

class MemberAdmin(admin.ModelAdmin):
    list_display = ('name','department', 'member_since','is_active')
    list_filter = ['department']
admin.site.register(Member, MemberAdmin)

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'start_date', 'open_invite', 'price_in_dkk', 'max_participants')
    date_hierarchy = 'start_date'
    #list_filter = ('department','open_invite')

    # Only view activities on own department
    def get_queryset(self, request):
        qs = super(ActivityAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        departments = Department.objects.filter(adminuserinformation__user=request.user)
        return qs.filter(department__in=departments)

    # Only show own departments when creating new activity
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if(db_field.name == 'department' and not request.user.is_superuser):
            kwargs["queryset"] = Department.objects.filter(adminuserinformation__user=request.user)
        return super(ActivityAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    fieldsets = (
        ('Afdeling', {'fields': (
            'department',
        )
        }
         ),
        ('Aktivitet',
            {'description' : '<p>Aktivitets navnet skal afspejle aktivitet samt tidspunkt. F.eks. <em>Forårs sæson 2016</em>.</p><p>Tidspunkt er f.eks. <em>Onsdage 17:00-19:00</em></p>',
            'fields': (
            'name',
            'open_hours',
            'description',
            'start_date',
            'end_date',
        )
        }
         ),
        ('Lokation og ansvarlig', {
            'description': '<p>Adresse samt ansvarlig kan adskille sig fra afdelingens informationer. (f.eks. et gamejam der foregår et andet sted)</p>',
            'fields': (
            'responsible_name',
            'responsible_contact',
            'streetname',
            'housenumber',
            'floor',
            'door',
            'zipcode',
            'city',
            'placename'
        )
        }
         ),

         ('Tilmeldings detaljer', {
         'description' : '<p>Tilmeldings instruktioner er tekst der kommer til at stå på betalings forularen på tilmeldings siden. Den skal bruges til at stille spørgsmål som den der tilmelder sig kan besvare ved tilmelding.</p><p>Fri tilmelding, betyder at alle kan når som helst tilmelde sig denne aktivitet - først til mølle. Dette er kun til arrangementer og klubaften-sæsoner i områder hvor der ikke er nogen venteliste. Alle arrangementer med fri tilmelding kommer til at stå med en stor "tilmeld" knap på medlems siden. <b>Vi bruger typisk ikke fri tilmelding - spørg i Slack hvis du er i tvivl!</b></p>',
         'fields' : (
            'instructions',
            'open_invite',
            'price_in_dkk',
            'signup_closing',
            'max_participants',
            'min_age',
            'max_age',
         )
         })
    )

    #inlines = [ActivityParticipantInline, ActivityInviteInline]
admin.site.register(Activity, ActivityAdmin)

class PersonInline(admin.TabularInline):

    def admin_link(self, instance):
        url = reverse('admin:%s_%s_change' % (instance._meta.app_label, instance._meta.model_name), args=(instance.id,))
        return format_html(u'<a href="{}">{}</a>', url, instance.name)
    admin_link.short_description = 'Navn'

    model = Person
    fields = ('admin_link', 'membertype', 'zipcode', 'added')
    readonly_fields = fields
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    fields = ('added', 'payment_type', 'confirmed_dtm', 'rejected_dtm', 'amount_ore')
    readonly_fields = ('family',)
    extra = 0

class ActivityParticipantInline(admin.TabularInline):
    model = ActivityParticipant
    extra = 0

    def get_queryset(self, request):
        return ActivityParticipant.objects.all()


class ActivityInviteInline(admin.TabularInline):
    model = ActivityInvite
    extra = 0

    # Limit the activity possible to invite to: Not finished and belonging to user
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if(db_field.name == 'activity' and not request.user.is_superuser):
            departments = Department.objects.filter(adminuserinformation__user=request.user)
            kwargs["queryset"] = Activity.objects.filter(end_date__gt=timezone.now(), department__in=departments)
        return super(ActivityInviteInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    # Only view invites it would be possible for user to give out
    def get_queryset(self, request):
        qs = super(ActivityInviteInline, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        departments = Department.objects.filter(adminuserinformation__user=request.user)
        return qs.filter(activity__end_date__gt=timezone.now(), activity__department__in=departments)

class MemberInline(admin.TabularInline):
    fields = ['department', 'member_since', 'member_until']
    readonly_fields = fields
    model = Member
    extra = 0

class FamilyAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        if(request.user.has_perm('members.view_family_unique')):
            return ('email', 'unique')
        else:
            return ('email',)
    search_fields = ('email',)
    inlines = [PersonInline, PaymentInline, EmailItemInline]
    #actions = ['create_new_uuid', 'resend_link_email'] # new UUID gets used accidentially
    actions = ['resend_link_email']

    fields = ('email', 'dont_send_mails', 'confirmed_dtm')
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

class ParticipantPaymentListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = 'Betaling'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'payment_list'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        activitys = [('none', 'Ikke betalt'), ('ok', 'Betalt'), ('pending', 'Afventende'), ('rejected', 'Afvist')]
        return activitys

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        if self.value() == 'none':
            return queryset.filter(payment__isnull=True)
        elif self.value() == 'ok':
            return queryset.filter(payment__isnull=False, payment__confirmed_dtm__isnull=False)
        elif self.value() == 'pending':
            return queryset.filter(payment__isnull=False, payment__confirmed_dtm__isnull=True)
        elif self.value() == 'rejected':
            return queryset.filter(payment__isnull=False, payment__rejected_dtm__isnull=False)

class ActivityParticipantListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = 'Efter aktivitet'

    # Parameter for the filter that will be used in the URL query.
    parameter_name='activity'

    def lookups(self, request, model_admin):
        activitys = []
        if request.user.is_superuser:
            departments = Department.objects.filter()
        else:
            departments = Department.objects.filter(adminuserinformation__user=request.user)

        for activity in Activity.objects.filter(department__in=departments).order_by('start_date').order_by('zipcode'):
            activitys.append(( str(activity.pk), str(activity)))
        return activitys

    def queryset(self, request, queryset):
        if(self.value() == None):
            return queryset
        else:
            return queryset.filter(activity=self.value())

class ActivityParticipantAdmin(admin.ModelAdmin):
    list_display = ['added_dtm', 'member', 'activity', 'note']
    list_filter = (ActivityParticipantListFilter,ParticipantPaymentListFilter)
    list_display_links = ('member',)
    search_fields = ('member__person__name', )

admin.site.register(ActivityParticipant, ActivityParticipantAdmin)


class ActivityInviteAdminForm(forms.ModelForm):
    class Meta:
        model = ActivityInvite
        exclude = []

    def __init__(self, *args, **kwds):
        super(ActivityInviteAdminForm, self).__init__(*args, **kwds)
        self.fields['person'].queryset = Person.objects.order_by(Lower('name'))

class ActivivtyInviteActivityListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = 'Aktiviteter'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'activity'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            departments = Department.objects.filter()
        else:
            departments = Department.objects.filter(adminuserinformation__user=request.user)

        activitys = []
        for activity in Activity.objects.filter(department__in=departments).order_by('zipcode'):
            activitys.append(( str(activity.pk), activity))

        return activitys

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        if self.value() == None:
            return queryset
        else:
            return queryset.filter(activity__pk=self.value())

class ActivityInviteAdmin(admin.ModelAdmin):
    list_display = ('person', 'activity', 'invite_dtm', 'person_age_years', 'person_zipcode', 'rejected_dtm')
    list_filter = (ActivivtyInviteActivityListFilter,)
    search_fields = ('person__name', )
    list_display_links = None
    form = ActivityInviteAdminForm

    # Limit the activity possible to invite to: Not finished and belonging to user
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if(db_field.name == 'activity' and not request.user.is_superuser):
            departments = Department.objects.filter(adminuserinformation__user=request.user)
            kwargs["queryset"] = Activity.objects.filter(end_date__gt=timezone.now(), department__in=departments)
        return super(ActivityInviteAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def person_age_years(self, item):
        return item.person.age_years()
    person_age_years.short_description = 'Alder'

    def person_zipcode(self, item):
        return item.person.zipcode
    person_zipcode.short_description = 'Postnummer'

admin.site.register(ActivityInvite, ActivityInviteAdmin)


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

        if request.user.is_superuser:
            department_queryset = Department.objects.filter(has_waiting_list=True).order_by('zipcode')
        else:
            department_queryset = Department.objects.filter(has_waiting_list=True, adminuserinformation__user=request.user).order_by('zipcode')

        departments = [('any', 'Alle opskrevne samlet'), ('none', 'Ikke skrevet på venteliste')]
        for department in department_queryset:
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

        if self.value() == 'any':
            return queryset.exclude(waitinglist__isnull=True)
        elif self.value() == 'none':
            return queryset.filter(waitinglist__isnull=True)
        elif self.value() == None:
            return queryset
        else:
            return queryset.filter(waitinglist__department__pk=self.value())

class PersonParticipantListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = 'Deltager på'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'participant_list'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            my_departments = Department.objects.filter()
        else:
            my_departments = Department.objects.filter(adminuserinformation__user=request.user)

        activitys = [('none', 'Deltager ikke'), ('any', 'Alle deltagere samlet')]
        for activity in Activity.objects.filter(department__in=my_departments).order_by('start_date').order_by('zipcode'):
            activitys.append(( str(activity.pk), str(activity)))

        return activitys

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        if(self.value() == 'none'):
            return queryset.filter(member__activityparticipant__isnull=True)
        elif(self.value() == 'any'):
            return queryset.exclude(member__activityparticipant__isnull=True)
        elif(self.value() == None):
            return queryset
        else:
            return queryset.filter(member__activityparticipant__activity=self.value())

class PersonInvitedListFilter(admin.SimpleListFilter):
    # Title shown in filter view
    title = 'Inviteret til'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'activity_invited_list'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        if request.user.is_superuser:
            my_departments = Department.objects.filter()
        else:
            my_departments = Department.objects.filter(adminuserinformation__user=request.user)

        activitys = [('none', 'Ikke inviteret til noget'), ('any', 'Alle inviterede')]
        for activity in Activity.objects.filter(department__in=my_departments).order_by('start_date').order_by('zipcode'):
            activitys.append(( str(activity.pk), str(activity)))

        return activitys

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        if(self.value() == 'none'):
            return queryset.filter(activityinvite__isnull=True)
        elif(self.value() == 'any'):
            return queryset.exclude(activityinvite__isnull=True)
        elif(self.value() == None):
            return queryset
        else:
            return queryset.filter(activityinvite__activity=self.value())


class WaitingListInline(admin.TabularInline):
    model = WaitingList
    fields = ['on_waiting_list_since', 'department', 'number_on_waiting_list']
    readonly_fields = fields
    extra = 0

class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'membertype', 'family_url', 'age_years', 'zipcode', 'added')
    list_filter = ('membertype', 'gender', PersonWaitinglistListFilter, PersonInvitedListFilter, PersonParticipantListFilter)
    search_fields = ('name', 'family__email',)
    actions = ['invite_to_own_activity', 'export_emaillist', 'export_csv']

    inlines = [PaymentInline, ActivityInviteInline, MemberInline, WaitingListInline]

    def family_url(self, item):
        return format_html(u'<a href="../family/%d">%s</a>' % (item.family.id, item.family.email))
    family_url.allow_tags = True
    family_url.short_description = 'Familie'

    # needs 'view_full_address' to set personal details.
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

    def unique(self, item):
        return item.family.unique if item.family != None else ''

    def invite_to_own_activity(self,request, queryset):
        return HttpResponse("Ikke klar endnu. Vi implementerer denne når vi får tid. Tryk på hver person for at invitere i stedet for.")
    invite_to_own_activity.short_description = "Inviter valgte personer til en aktivitet"

    def export_emaillist(self,request, queryset):
        result_string = "kopier denne liste direkte ind i dit email program (Husk at bruge Bcc!)\n\n"
        family_email = []
        for person in queryset:
            family_email.append(person.family.email)
        result_string = result_string + ';\n'.join(list(set(family_email)))
        result_string = result_string + "\n\n\nHusk nu at bruge Bcc! ... IKKE TO: og heller IKKE CC: felterne\n\n"

        return HttpResponse(result_string, content_type="text/plain")
    export_emaillist.short_description = "Exporter e-mail liste"

    def export_csv(self,request, queryset):
        result_string = '"Navn";"Alder";"Opskrevet";"Tlf (barn)";"Email (barn)";"Tlf (forælder)";"Email (familie)"\n'
        for person in queryset:
            parent = person.family.get_first_parent()
            if parent:
                parent_phone=parent.phone
            else:
                parent_phone=""

            result_string = result_string + person.name + ";" + str(person.age_years()) + ";" + str(person.added) + ";" + person.phone + ";" + person.email + ";" + parent_phone + ";" + person.family.email + "\n"
            response = HttpResponse(result_string, content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename="personer.csv"'
        return response
    export_csv.short_description = "Exporter CSV"

admin.site.register(Person,PersonAdmin)

admin.site.register(EmailTemplate)

class AdminUserInformationInline(admin.StackedInline):
    model = AdminUserInformation
    filter_horizontal = ('departments',)
    can_delete = False

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (AdminUserInformationInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'added', 'payment_type', 'amount_ore', 'family', 'confirmed_dtm', 'cancelled_dtm', 'rejected_dtm', 'activityparticipant']
    list_filter = ['payment_type', 'activity']
    date_hierarchy = 'added'
    search_fields = ('family__email',)
    select_related = ('activityparticipant')

admin.site.register(Payment, PaymentAdmin)
#admin.site.register(QuickpayTransaction)
