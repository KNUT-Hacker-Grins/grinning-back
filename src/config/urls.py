from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 기존 urlpatterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/classify/', include('apps.ai_gateway.urls')),
    path('api/chat/', include('apps.chat.messaging.urls')), 
    path('api/chatbot/', include('apps.chat.chatbot.urls')),
    path('api/question/', include('apps.chat.questionnaire.urls')), 
    path('api/', include('apps.accounts.urls')),
    path('api/found-items/', include('apps.lostfound.found_items.urls')), 
    path('api/lost-items/', include('apps.lostfound.lost_items.urls')),
    path('api/', include('apps.lostfound.reports.urls')),
    path('api/stats/', include('apps.lost_insight.urls')),
    path('api/map/', include('apps.map_api.urls')),
    path('api/upload/', include('apps.uploads.urls')),
    path('api/police/', include('apps.police.urls')),
]

# 개발환경에서만 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
