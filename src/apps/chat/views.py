from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,  pagination
from django.shortcuts import get_object_or_404
from .models import ChatRoom
from ..found_items.models import FoundItem
from ..lost_items.models import LostItem
from .serializers import ChatRoomSerializer
from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer

class StartChatView(APIView):
    def post(self, request):
        post_id = request.data.get("post_id")
        post_type = request.data.get("post_type")

        if post_type not in ["found", "lost"]:
            return Response({"status": "error", "message": "유효하지 않은 post_type"}, status=400)

        # 1. 게시글 객체 가져오기
        PostModel = FoundItem if post_type == "found" else LostItem
        post = get_object_or_404(PostModel, id=post_id)

        # 2. 이미 해당 post에 대해 생성된 채팅방 있는지 확인
        existing = ChatRoom.objects.filter(
            post_type=post_type,
            post_id=post_id,
            participants=request.user
        ).filter(participants=post.user).first()

        if existing:
            serializer = ChatRoomSerializer(existing)
            return Response({
                "status": "success",
                "code": 200,
                "data": {
                    "room_id": existing.id,
                    "participants": serializer.data["participants"]
                },
                "message": "기존 채팅방 반환"
            })

        # 3. 새 채팅방 생성
        room = ChatRoom.objects.create(post_type=post_type, post_id=post_id)
        room.participants.add(request.user, post.user)
        room.save()

        serializer = ChatRoomSerializer(room)
        return Response({
            "status": "success",
            "code": 201,
            "data": {
                "room_id": str(room.id),
                "participants": serializer.data["participants"]
            },
            "message": "채팅방 생성 완료"
        }, status=201)

class ChatMessagePagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'

class ChatMessageList(APIView):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        messages = ChatMessage.objects.filter(room=room).order_by('-timestamp')
        paginator = ChatMessagePagination()
        page = paginator.paginate_queryset(messages, request)
        serializer = ChatMessageSerializer(page, many=True)
        return paginator.get_paginated_response({
            'status': 'success',
            'code': 200,
            'data': {
                'messages': serializer.data,
                'page': int(request.query_params.get('page', 1)),
                'total': messages.count()
            },
            'message': '조회 성공'
        })

class ChatMessageCreate(APIView):
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

