from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'foreningsmedlemmer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    path(r"^admin/", admin.site.urls),
    path(r"^", include("members.urls")),
    path("^sentry-debug/", lambda request: 1 / 0),  # Test url, delete this
]
