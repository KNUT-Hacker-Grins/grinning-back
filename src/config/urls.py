from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 기존 urlpatterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/classify/', include('core.ai_gateway.image_classifier.urls')),
    path('api/translation/', include('core.ai_gateway.translation.urls')),
    path('api/chat/', include('core.features.chat.chat.urls')), 
    path('api/chatbot/', include('core.features.chat.chatbot.urls')), 
    path('api/', include('core.features.accounts.urls')),
    path('api/found-items/', include('core.features.lostfound.found_items.urls')), 
    path('api/lost-items/', include('core.features.lostfound.lost_items.urls')),
    path('api/', include('core.features.lostfound.reports.urls')),
    path('api/lost-insight/', include('core.integrations.lost_insight.urls')),
    path('api/map/', include('core.integrations.map_api.urls')),
    path('api/upload/', include('core.integrations.uploads.urls')),
    path('api/police/', include('core.integrations.police.urls')),
]

# 개발환경에서만 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
