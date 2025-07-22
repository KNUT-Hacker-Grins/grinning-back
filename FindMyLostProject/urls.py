from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from found_items.views import FoundItemViewSet

# DRF Router 등록
router = DefaultRouter()
router.register(r'api/found-items', FoundItemViewSet, basename='founditem')

# 기존 urlpatterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/upload/', include('uploads.urls')),
    path('api/lost-items/', include('lost_items.urls')),
]

# DRF router 기반 url 추가
urlpatterns += router.urls

# 개발환경에서만 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
