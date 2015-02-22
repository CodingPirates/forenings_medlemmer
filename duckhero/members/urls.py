from django.conf.urls import patterns,  url
from members.views import FamilyCreate, FamilyUpdate

urlpatterns = patterns('',
    url(r'family/$', FamilyCreate.as_view(), name='family_add'),
    url(r'family/(?P<pk>[\w-]+)$', FamilyUpdate.as_view(), name='family_update'),
)
