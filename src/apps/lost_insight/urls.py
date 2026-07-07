from django.urls import path
from .views import LostInsightRecommendView

urlpatterns = [
    path('popular-categories', LostInsightRecommendView.as_view(), name='lost_insight_recommend'),
]