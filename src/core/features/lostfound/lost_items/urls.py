from django.urls import path
from .views import *

urlpatterns = [
    path('', create_lost_item, name='create_lost_item'),
    path('list', lost_items_list, name='lost_items_list'),
    path('search', lost_items_list_by_search, name='lost_items_list_by_search'),
    path('<int:id>/', lost_item_detail, name='lost_item_detail'),
    path('<int:id>/edit', update_lost_item, name='update_lost_item'),
    path('<int:id>/delete', delete_lost_item, name='delete_lost_item'),
    path('<int:id>/status', update_lost_item_status, name='update_status'),
    path('admin', admin_lost_items_list, name='admin_lost_items_list'),
    path('admin/<int:id>', admin_delete_lost_item, name='admin_delete_lost_item'),
]
