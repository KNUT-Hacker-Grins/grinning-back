from django.urls import path
from .views import ChatMessageList, ChatMessageCreate, StartChatView

urlpatterns = [
    path('chat/start', StartChatView.as_view(), name='start_chat'),
    path('chat/<int:room_id>/messages', ChatMessageList.as_view(), name='chat_message_list'),
    path('chat/<int:room_id>/message', ChatMessageCreate.as_view(), name='chat_message_create'),
]