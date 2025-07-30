from django.shortcuts import get_object_or_404

from rest_framework import pagination
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.chat.models import ChatRoom, ChatMessage
from apps.chat.serializers import ChatMessageSerializer

class ChatMessagePagination(pagination.PageNumberPagination):
    page_size = 20  # 원하는 기본 페이지 크기
    page_size_query_param = 'limit'

class ChatMessageListView(APIView):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        if request.user not in room.participants.all():
            return Response({"detail": "접근 권한 없음"}, status=403)

        messages = ChatMessage.objects.filter(room=room).order_by('-timestamp')
        paginator = ChatMessagePagination()
        page = paginator.paginate_queryset(messages, request)
        serializer = ChatMessageSerializer(page, many=True)

        return paginator.get_paginated_response({
            "status": "success",
            "code": 200,
            "data": {
                "messages": serializer.data,
                "page": paginator.page.number,
                "total": paginator.page.paginator.count
            },
            "message": "조회 성공"
        })

