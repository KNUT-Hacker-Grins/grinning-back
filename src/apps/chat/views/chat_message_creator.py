from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.chat.models import ChatRoom
from apps.chat.serializers import ChatMessageSerializer

class ChatMessageCreateView(APIView):
    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(sender=request.user, room=room)
            return Response({
                'status': 'success',
                'code': 201,
                'data': ChatMessageSerializer(message).data,
                'message': '전송 완료'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



