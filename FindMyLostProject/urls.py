"""
URL configuration for FindMyLostProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin

# urlpatterns = [
#     path("admin/", admin.site.urls),
# ]

from django.urls import path
from rest_framework.routers import DefaultRouter
from found_items.views import FoundItemViewSet

"""
REST API 엔드포인트(리소스)는 관습적으로 슬래시로 끝남

예: /api/items/, /api/users/

router.register('api/items', ItemViewSet)
이 경우 실제 등록되는 URL은 /api/items/ (마지막에 슬래시!)

즉, POST /api/items/ ← 이게 정상 경로
Django REST framework의 ViewSet/Router를 쓰면 무조건 슬래시 있는 엔드포인트만 자동 생성됨

"""
router = DefaultRouter()
router.register(r'api/found-items', FoundItemViewSet, basename='lostitem')

urlpatterns = []
urlpatterns += router.urls
