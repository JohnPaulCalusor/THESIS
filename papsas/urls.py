# papsas/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from papsas_app.api.views_health import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="root-health-check"),
    path("api/", include("papsas_api.urls")),
    path("api/", include("papsas_app.api.urls")),
    path("", include("papsas_app.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
