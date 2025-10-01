from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .health import health
from .views import ElectionViewSet
from .views_auth import EmailTokenObtainPairView, TokenRefreshView, UsersMeView

router = DefaultRouter()
router.register(r"elections", ElectionViewSet, basename="elections")

urlpatterns = [
    # Health
    path("health", health), path("health/", health),

    # Auth (SimpleJWT; accepts {"email": "...", "password": "..."})
    path("auth/login", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/login/", EmailTokenObtainPairView.as_view()),
    path("auth/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/refresh/", TokenRefreshView.as_view()),

    # Users
    path("users/me", UsersMeView.as_view()),
    path("users/me/", UsersMeView.as_view()),

    # DRF router endpoints
    path("", include(router.urls)),
]
