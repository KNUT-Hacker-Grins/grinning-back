
# lost_items/urls.py (새로 생성)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_lost_item, name='create_lost_item'),
]
