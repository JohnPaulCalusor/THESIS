from django.urls import include, path
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import ElectionViewSet

router = DefaultRouter()
router.register(r"elections", ElectionViewSet, basename="elections")

def health_view(_request):
    return JsonResponse({"ok": True})

urlpatterns = [
    path("health", health_view, name="api-health"),
    path("", include(router.urls)),
]
