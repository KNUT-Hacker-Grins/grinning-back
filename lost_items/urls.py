
# lost_items/urls.py (새로 생성)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_lost_item, name='create_lost_item'),
    path('my', views.my_lost_items, name='my_lost_items'),
    path('<uuid:id>', views.lost_item_detail, name='lost_item_detail'),
    path('<uuid:id>/edit', views.update_lost_item, name='update_lost_item'),
    path('<uuid:id>/delete', views.delete_lost_item, name='delete_lost_item'),
    path('<uuid:id>/status', views.update_lost_item_status, name='update_status'),
]