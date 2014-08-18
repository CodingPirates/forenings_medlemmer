from django.contrib import admin

from medlemmer.models import Address
from medlemmer.models import Phonenumber
from medlemmer.models import EmailAdress
from medlemmer.models import Person
from medlemmer.models import Foto
from medlemmer.models import Department
from medlemmer.models import Activity
from medlemmer.models import ActivityDate
from medlemmer.models import ActivitySignup
from medlemmer.models import ActivityMeet
from medlemmer.models import Payment

# Register your models here.
admin.site.register(Address)
admin.site.register(Phonenumber)
admin.site.register(EmailAdress)
admin.site.register(Person)
admin.site.register(Foto)
admin.site.register(Department)
admin.site.register(Activity)
admin.site.register(ActivityDate)
admin.site.register(ActivitySignup)
admin.site.register(ActivityMeet)
admin.site.register(Payment)
