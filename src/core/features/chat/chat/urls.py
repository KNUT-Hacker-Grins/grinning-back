from django.urls import path
from .views import ( 
    ChatMessageListView, 
    ChatMessageCreateView, 
    StartChatView, 
    MarkAsReadView, 
    UnreadCountView,
    ChatRoomListView
)

urlpatterns = [
    path('start', StartChatView.as_view(), name='start_chat'),
    path('rooms', ChatRoomListView.as_view(), name='chat-room-list'),
    path('<int:room_id>/messages', ChatMessageListView.as_view(), name='chat_message_list'),
    path('<int:room_id>/message', ChatMessageCreateView.as_view(), name='chat_message_create'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
    path('mark-as-read/<int:room_id>/', MarkAsReadView.as_view(), name='mark-as-read'),
]
