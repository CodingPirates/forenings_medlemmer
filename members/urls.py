from django.conf.urls import patterns,  url
from members.views import FamilyCreate, Details, PersonCreate, PersonUpdate

urlpatterns = patterns('',
    url(r'^$', FamilyCreate.as_view(), name='family_add'),
    url(r'(?P<unique>[\w-]+)/Person/(?P<pk>[\d])/$', PersonUpdate.as_view(), name='person_update'),
    url(r'(?P<unique>[\w-]+)/Person/$', PersonCreate.as_view(), name='person_add'),
    url(r'(?P<unique>[\w-]+)$', Details, name='family_detail'),
)
