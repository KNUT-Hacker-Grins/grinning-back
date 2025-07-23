from rest_framework.routers import DefaultRouter
from .views import FoundItemViewSet

router = DefaultRouter()
router.register(r'', FoundItemViewSet, basename='founditem')  # 'api/found-items' ❌

urlpatterns = router.urls