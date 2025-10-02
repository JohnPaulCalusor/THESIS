from rest_framework.routers import DefaultRouter
from .views import ElectionViewSet

router = DefaultRouter()
router.register(r"elections", ElectionViewSet, basename="elections")

urlpatterns = router.urls
