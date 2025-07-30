from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.chat.models import ChatRoom, ChatMessage

class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        rooms = ChatRoom.objects.filter(participants=user)

        unread_by_room = {}
        for room in rooms:
            unread_count = ChatMessage.objects.filter(
                room=room,
                is_read=False
            ).exclude(sender=user).count()  # 내가 보낸 건 제외해야 진짜 '수신 안읽음'
            if unread_count > 0:
                unread_by_room[str(room.id)] = unread_count

        return Response(unread_by_room)

