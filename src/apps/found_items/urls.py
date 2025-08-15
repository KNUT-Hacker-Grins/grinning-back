from django.urls import path
from .views import (
    FoundItemCreateView, FoundItemListView, FoundItemDetailView,
    FoundItemUpdateView, FoundItemDeleteView, FoundItemStatusUpdateView,
    AdminFoundItemListView
)

urlpatterns = [
    path('', FoundItemCreateView.as_view(), name='founditem_create'),
    path('list', FoundItemListView.as_view(), name='founditem_list'),
    path('<int:id>/', FoundItemDetailView.as_view(), name='founditem_detail'),
    path('<int:id>/edit', FoundItemUpdateView.as_view(), name='founditem_update'),
    path('<int:id>/delete', FoundItemDeleteView.as_view(), name='founditem_delete'),
    path('<int:id>/status', FoundItemStatusUpdateView.as_view(), name='founditem_status_update'),
    path('admin', AdminFoundItemListView.as_view(), name='admin_founditem_list')
]
