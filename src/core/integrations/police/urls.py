from django.urls import path
from .views import PoliceFoundItemsView, PoliceLostItemsView

urlpatterns = [
    path('found-items/', PoliceFoundItemsView.as_view(), name='police_found_items'),
    path('lost-items/', PoliceLostItemsView.as_view(), name='police_lost_items'),
]
