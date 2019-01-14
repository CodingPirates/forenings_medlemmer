from django.conf.urls import url
from members.views import FamilyDetails, PersonCreate, PersonUpdate, WaitingListSetSubscription, DeclineInvitation, EntryPage, loginEmailSent, ConfirmFamily, QuickpayCallback, ActivitySignup, \
    waitinglistView, paymentGatewayErrorView, volunteerSignup, departmentView
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', EntryPage, name='entry_page'),
    url(r'^account/login/$', auth_views.login, {'template_name': 'members/login.html'}, name='person_login'),
    url(r'^account/logout/$', auth_views.logout, {'next_page': '/'}, name='person_logout'),
    url(r'volunteer$', volunteerSignup, name='volunteer_signup'),
    url(r'login_email_sent/$', loginEmailSent, name='login_email_sent'),
    url(r'family/$', FamilyDetails, name='family_detail'),
    url(r'family/Person/(?P<id>[\d]+)/$', PersonUpdate, name='person_update'),
    url(r'family/Person/(?P<membertype>[A-Z]{2})$', PersonCreate, name='person_add'),
    url(r'family/activity/(?P<activity_id>[\d]+)/person/(?P<person_id>[\d]+)/$', ActivitySignup, name='activity_signup'),
    url(r'family/activity/(?P<activity_id>[\d]+)/person/(?P<person_id>[\d]+)/view/$', ActivitySignup, name='activity_view_person'),
    url(r'family/activity/(?P<activity_id>[\d]+)/view/$', ActivitySignup, name='activity_view_family'),
    url(r'family/invitation_decline/(?P<invitation_id>[\d]+)/$', DeclineInvitation, name='invitation_decline'),
    url(r'family/waitinglist$', waitinglistView, name='family_waitinglist_view'),
    url(r'family/payment_gateway_error$', paymentGatewayErrorView, name='payment_gateway_error_view'),
    url(r'confirm_details/$', ConfirmFamily, name='confirm_details'),
    url(r'waiting_list/(?P<id>[\d]+)/(?P<departmentId>[\d]+)/(?P<action>(subscribe|unsubscribe))/$', WaitingListSetSubscription, name='waiting_list_subscription'),
    url(r'^activity/(?P<activity_id>[\d]+)/$', ActivitySignup, name='activity_view'),
    url(r'quickpay_callback$', QuickpayCallback, name='quickpay_callback'),
    url(r'waitinglist$', waitinglistView, name='waitinglist_view'),
    url(r'departments$', departmentView, name='department_view'),
]
