from django.conf.urls import patterns,  url
from members.views import FamilyDetails, PersonCreate, PersonUpdate, AcceptInvitation, WaitingListSetSubscription, DeclineInvitation, InviteDetails, EntryPage, loginEmailSent, ConfirmFamily, QuickpayCallback

urlpatterns = patterns('',
    url(r'^/{0,1}$', EntryPage, name='entry_page'),
    url(r'login_email_sent/$', loginEmailSent, name='login_email_sent'),
    url(r'family/(?P<unique>[\w-]+)/$', FamilyDetails, name='family_detail'),
    url(r'invite/(?P<unique>[\w-]+)/accept/$', AcceptInvitation, name='invite_accept'),
    url(r'confirm_details/(?P<unique>[\w-]+)/$', ConfirmFamily, name='confirm_details'),
    url(r'waiting_list/(?P<unique>[\w-]+)/(?P<id>[\d]+)/(?P<departmentId>[\d]+)/(?P<action>(subscribe|unsubscribe))/$', WaitingListSetSubscription, name='waiting_list_subscription'),
    url(r'invite/(?P<unique>[\w-]+)/decline/$', DeclineInvitation, name='invite_decline'),
    url(r'invite/(?P<unique>[\w-]+)/$', InviteDetails, name='invite_detail'),
    url(r'family/(?P<unique>[\w-]+)/Person/(?P<id>[\d]+)/$', PersonUpdate, name='person_update'),
    url(r'family/(?P<unique>[\w-]+)/Person/(?P<membertype>[A-Z]{2})$', PersonCreate, name='person_add'),
    url(r'quickpay_callback$', QuickpayCallback, name='quickpay_callback'),
)
