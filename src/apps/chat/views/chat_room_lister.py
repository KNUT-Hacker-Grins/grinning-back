from django.utils.timezone import localtime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.chat.models import ChatRoom, ChatMessage

class ChatRoomListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        rooms = ChatRoom.objects.filter(participants=user).distinct()

        result = []
        for room in rooms:
            last_message = (
                ChatMessage.objects.filter(room=room)
                .order_by('-timestamp')
                .first()
            )

            unread_count = ChatMessage.objects.filter(
                room=room,
                is_read=False
            ).exclude(sender=user).count()

            other_user = room.participants.exclude(id=user.id).first()
            result.append({
                "room_id": str(room.id),
                "other_user": {
                    "id": other_user.social_id,
                    "name": other_user.name,
                    "email": other_user.email,
                } if other_user else None,
                "last_message": last_message.content if last_message else None,
                "last_timestamp": localtime(last_message.timestamp).isoformat() if last_message else None,
                "unread_count": unread_count,
            })

        return Response(result)