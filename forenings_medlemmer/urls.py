from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'foreningsmedlemmer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r"^admin/", admin.site.urls),
    url(r"^", include("members.urls")),
    url("^sentry-debug/", lambda request: 1 / 0),  # Test url, delete this
]
