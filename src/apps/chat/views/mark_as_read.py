from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.chat.models import ChatRoom, ChatMessage

class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id, *args, **kwargs):
        user = request.user

        try:
            room = ChatRoom.objects.get(id=room_id, participants=user)
        except ChatRoom.DoesNotExist:
            return Response({'detail': '채팅방이 존재하지 않거나 권한이 없습니다.'}, status=404)

        updated_count = ChatMessage.objects.filter(
            room=room,
            is_read=False
        ).exclude(sender=user).update(is_read=True)

        return Response({
            'message': '읽음 처리 완료',
            'updated': updated_count
        })