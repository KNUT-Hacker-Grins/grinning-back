from django.urls import path
from .views import *

urlpatterns = [
    path('', create_lost_item, name='create_lost_item'),
    path('my', my_lost_items, name='my_lost_items'),
    path('<uuid:id>', lost_item_detail, name='lost_item_detail'),
    path('<uuid:id>/edit', update_lost_item, name='update_lost_item'),
    path('<uuid:id>/delete', delete_lost_item, name='delete_lost_item'),
    path('<uuid:id>/status', update_lost_item_status, name='update_status'),
]
