from django.urls import path
from .views import MapItemsView

urlpatterns = [
    path('items/', MapItemsView.as_view(), name='map_items'),
]