from django.urls import path
from .views import PoliceFoundItemsView

urlpatterns = [
    path('found-items/', PoliceFoundItemsView.as_view(), name='police_found_items'),
]
