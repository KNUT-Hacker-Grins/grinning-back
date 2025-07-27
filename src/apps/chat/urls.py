from django.urls import path
from .views import ( 
    ChatMessageList, 
    ChatMessageCreate, 
    StartChatView, 
    MarkAsReadView, 
    UnreadCountView
)

urlpatterns = [
    path('start', StartChatView.as_view(), name='start_chat'),
    path('<int:room_id>/list', ChatMessageList.as_view(), name='chat_message_list'),
    path('<int:room_id>/message', ChatMessageCreate.as_view(), name='chat_message_create'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
    path('mark-as-read/<int:room_id>/', MarkAsReadView.as_view(), name='mark-as-read')
]
