from django.conf.urls import patterns,  url
from members.views import FamilyCreate, FamilyDetails, PersonCreate, PersonUpdate, AcceptInvitation, DeclineInvitation, InviteDetails

urlpatterns = patterns('',
    url(r'invite/(?P<unique>[\w-]+)/accept/$', AcceptInvitation, name='invite_accept'),
    url(r'invite/(?P<unique>[\w-]+)/decline/$', DeclineInvitation, name='invite_decline'),
    url(r'invite/(?P<unique>[\w-]+)/$', InviteDetails, name='invite_detail'),
    url(r'family/$', FamilyCreate.as_view(), name='family_add'),
    url(r'family/(?P<unique>[\w-]+)/Person/(?P<id>[\d]+)/$', PersonUpdate, name='person_update'),
    url(r'family/(?P<unique>[\w-]+)/Person/(?P<membertype>[A-Z]{2})$', PersonCreate, name='person_add'),
    url(r'family/(?P<unique>[\w-]+)/$', FamilyDetails, name='family_detail'),
)
