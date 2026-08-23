from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/library/", include("apps.library.urls")),
    path("api/org/", include("apps.org.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/meetings/", include("apps.meetings.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
