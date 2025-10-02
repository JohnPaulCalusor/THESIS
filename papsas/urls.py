# papsas/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def health(_request):
    # keep this import-free so health works even if app imports fail
    return JsonResponse({"ok": True})

urlpatterns = [
    # Auth & user endpoints (you already had these here)
    path("api/", include("papsas_api.urls")),
    # Your app API (elections + health)
    path("api/", include("papsas_app.api.urls")),
    # HTML pages, if any
    path("", include("papsas_app.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
