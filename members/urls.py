from django.conf.urls import patterns,  url
from members.views import FamilyDetails, PersonCreate, PersonUpdate, WaitingListSetSubscription, DeclineInvitation, EntryPage, loginEmailSent, ConfirmFamily, QuickpayCallback, ActivitySignup, \
    waitinglistView

urlpatterns = patterns('',
    url(r'^/{0,1}$', EntryPage, name='entry_page'),
    url(r'login_email_sent/$', loginEmailSent, name='login_email_sent'),
    url(r'family/(?P<unique>[\w-]+)/$', FamilyDetails, name='family_detail'),
    url(r'family/(?P<unique>[\w-]+)/Person/(?P<id>[\d]+)/$', PersonUpdate, name='person_update'),
    url(r'family/(?P<unique>[\w-]+)/Person/(?P<membertype>[A-Z]{2})$', PersonCreate, name='person_add'),
    url(r'family/(?P<unique>[\w-]+)/activity/(?P<activity_id>[\d]+)/person/(?P<person_id>[\d]+)/$', ActivitySignup, name='activity_signup'),
    url(r'family/(?P<unique>[\w-]+)/activity/(?P<activity_id>[\d]+)/person/(?P<person_id>[\d]+)/view/$', ActivitySignup, name='activity_view_person'),
    url(r'family/(?P<unique>[\w-]+)/invitation_decline/(?P<invitation_id>[\d]+)/$', DeclineInvitation, name='invitation_decline'),
    url(r'confirm_details/(?P<unique>[\w-]+)/$', ConfirmFamily, name='confirm_details'),
    url(r'waiting_list/(?P<unique>[\w-]+)/(?P<id>[\d]+)/(?P<departmentId>[\d]+)/(?P<action>(subscribe|unsubscribe))/$', WaitingListSetSubscription, name='waiting_list_subscription'),
    url(r'^activity/(?P<activity_id>[\d]+)/$', ActivitySignup, name='activity_view'),
    url(r'quickpay_callback$', QuickpayCallback, name='quickpay_callback'),
    url(r'waitinglist$', waitinglistView, name='waitinglist_view'),

)
