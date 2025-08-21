from django.urls import path
from .views import ChatbotMessageView, ChatbotHealthView

urlpatterns = [
    path('session/start', ChatbotMessageView.as_view(), name='chatbot_message'),
    path('health', ChatbotHealthView.as_view(), name='chatbot_health'),
]