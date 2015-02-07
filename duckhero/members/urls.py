from django.conf.urls import patterns,  url
from members import views
urlpatterns = patterns('',
    url(r'^$',views.index,name='index'),
    url(r'^(?P<person_guid>[-\w]+)$',views.person,name='person'),
)
