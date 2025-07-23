from django.urls import path
from .views import (
    FoundItemCreateView, FoundItemListView, FoundItemDetailView,
    FoundItemUpdateView, FoundItemDeleteView, FoundItemStatusUpdateView
)

urlpatterns = [
    path('', FoundItemCreateView.as_view(), name='founditem_create'),
    path('', FoundItemListView.as_view(), name='founditem_list'),
    path('<uuid:id>/', FoundItemDetailView.as_view(), name='founditem_detail'),
    path('<uuid:id>/edit/', FoundItemUpdateView.as_view(), name='founditem_update'),
    path('<uuid:id>/delete/', FoundItemDeleteView.as_view(), name='founditem_delete'),
    path('<uuid:id>/status/', FoundItemStatusUpdateView.as_view(), name='founditem_status_update'),
]
