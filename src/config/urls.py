from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 기존 urlpatterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/chat/', include('apps.features.chat.chat.urls')), 
    # path('api/chatbot/', include('apps.features.chat.chatbot.urls')), 
    path('api/found-items/', include('apps.features.lostfound.found_items.urls')), 
    path('api/lost-items/', include('apps.features.lostfound.lost_items.urls')),
    path('api/', include('apps.features.lostfound.reports.urls')),
    path('api/', include('apps.identity.accounts.urls')),
    path('api/classify/', include('apps.ml.image_classifier.urls')),
    path('api/translation/', include('apps.ml.translation.urls')),
    path('api/map/', include('apps.integrations.map_api.urls')),
    path('api/upload/', include('apps.integrations.uploads.urls')),
]

# 개발환경에서만 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
