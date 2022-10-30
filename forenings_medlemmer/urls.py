from django.urls import include, re_path
from django.contrib import admin

urlpatterns = [
    # Examples:
    # re_path(r'^$', 'foreningsmedlemmer.views.home', name='home'),
    # re_path(r'^blog/', include('blog.urls')),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^", include("members.urls")),
    re_path("^sentry-debug/", lambda request: 1 / 0),  # Test url, delete this
]
