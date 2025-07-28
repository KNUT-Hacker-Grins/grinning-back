from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 기존 urlpatterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/upload/', include('apps.uploads.urls')),
    path('api/lost-items/', include('apps.lost_items.urls')),
    path('api/found-items/', include('apps.found_items.urls')), 
    path('api/chat/', include('apps.chat.urls')), 
    path('api/', include('apps.reports.urls')),
    path('api/classify/', include('apps.classifier_api.urls')),
    path('api/translation/', include('apps.translation.urls')),
    path('api/', include('apps.accounts.urls')),
]

# 개발환경에서만 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
