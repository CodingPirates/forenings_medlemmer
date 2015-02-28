from django.conf.urls import patterns,  url
from members.views import FamilyCreate, Details, PersonCreate, PersonUpdate, AcceptInvitation

urlpatterns = patterns('',
    url(r'/invite/(?P<unique>[\w-]+)/accept/$', AcceptInvitation, name='invite_accept'),
    url(r'^$', FamilyCreate.as_view(), name='family_add'),
    url(r'(?P<unique>[\w-]+)/Person/(?P<id>[\d])/$', PersonUpdate, name='person_update'),
    url(r'(?P<unique>[\w-]+)/Person/$', PersonCreate, name='person_add'),
    url(r'(?P<unique>[\w-]+)/$', Details, name='family_detail'),

)
