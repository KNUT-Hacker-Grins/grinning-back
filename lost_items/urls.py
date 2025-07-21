
# lost_items/urls.py (새로 생성)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_lost_item, name='create_lost_item'),  # POST /api/lost-items/
    path('my', views.my_lost_items, name='my_lost_items'),     # GET /api/lost-items/my
    path('<uuid:id>', views.lost_item_detail, name='lost_item_detail'),
    path('<uuid:id>/edit', views.update_lost_item, name='update_lost_item'), # PUT /api/lost-items/{id}/edit
]