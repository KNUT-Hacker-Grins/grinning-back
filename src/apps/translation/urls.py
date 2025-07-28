from django.urls import path
from .views import TranslateAPIView

urlpatterns = [
    path("", TranslateAPIView.as_view(), name="translate")
]