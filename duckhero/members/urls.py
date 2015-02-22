from django.conf.urls import patterns,  url
from members.views import FamilyCreate, Details

urlpatterns = patterns('',
    url(r'^$', FamilyCreate.as_view(), name='family_add'),
    url(r'(?P<unique>[\w-]+)/$', Details, name='family_detail'),
)
