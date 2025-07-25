from django.urls import path
from .views import ChatMessageList, ChatMessageCreate, StartChatView

urlpatterns = [
    path('start', StartChatView.as_view(), name='start_chat'),
    path('<int:room_id>/list', ChatMessageList.as_view(), name='chat_message_list'),
    path('<int:room_id>/message', ChatMessageCreate.as_view(), name='chat_message_create'),
]