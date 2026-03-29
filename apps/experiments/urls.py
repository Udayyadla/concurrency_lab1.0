from rest_framework.routers import DefaultRouter
from .views import ExperimentRunViewSet

router = DefaultRouter()
router.register(r"experiments", ExperimentRunViewSet, basename="experiments")

urlpatterns = router.urls
