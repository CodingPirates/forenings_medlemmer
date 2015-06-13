from django.conf.urls import patterns,  url
from members.views import FamilyDetails, PersonCreate, PersonUpdate, AcceptInvitation, AcceptWaitingList, DeclineInvitation, InviteDetails, EntryPage, loginEmailSent

urlpatterns = patterns('',
    url(r'^/{0,1}$', EntryPage, name='entry_page'),
    url(r'login_email_sent/$', loginEmailSent, name='login_email_sent'),
    url(r'family/(?P<unique>[\w-]+)/$', FamilyDetails, name='family_detail'),
    url(r'invite/(?P<unique>[\w-]+)/accept/$', AcceptInvitation, name='invite_accept'),
    url(r'waiting_list/(?P<unique>[\w-]+)/(?P<id>[\d]+)/(?P<departmentId>[\d]+)/accept/$', AcceptWaitingList, name='waiting_list_accept'),
    url(r'invite/(?P<unique>[\w-]+)/decline/$', DeclineInvitation, name='invite_decline'),
    url(r'invite/(?P<unique>[\w-]+)/$', InviteDetails, name='invite_detail'),
    url(r'family/(?P<unique>[\w-]+)/Person/(?P<id>[\d]+)/$', PersonUpdate, name='person_update'),
    url(r'family/(?P<unique>[\w-]+)/Person/(?P<membertype>[A-Z]{2})$', PersonCreate, name='person_add'),
    url(r'family/(?P<unique>[\w-]+)/$', FamilyDetails, name='family_detail'),
)
