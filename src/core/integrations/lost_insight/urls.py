from django.urls import path
from .views import LostInsightRecommendView

urlpatterns = [
    path('', LostInsightRecommendView.as_view(), name='lost_insight_recommend'),
]