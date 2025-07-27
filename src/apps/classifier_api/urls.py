from django.urls import path
from .views import ClassificationView

urlpatterns = [
    path('', ClassificationView.as_view(), name='classify_image'),
]
