from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 기존 urlpatterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/upload/', include('uploads.urls')),
    path('api/lost-items/', include('lost_items.urls')),
    path('api/found-items/', include('found_items.urls')),  # 이게 핵심!
    path('api/', include('accounts.urls')),
]

# 개발환경에서만 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
