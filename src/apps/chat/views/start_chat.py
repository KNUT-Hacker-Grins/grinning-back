from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, pagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from apps.chat.models import ChatRoom
from apps.found_items.models import FoundItem
from apps.lost_items.models import LostItem
from apps.chat.serializers import ChatRoomSerializer
from apps.chat.models import ChatRoom, ChatMessage
from apps.chat.serializers import ChatMessageSerializer

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
            post_id=post_id
        ).first()
    
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
        if request.user == post.user:
            return Response(
                {
                    "status": "fail",
                    "code": 403,
                    "message": "자신의 글에는 채팅을 시작할 수 없습니다."
                },
                status=403
            )
        
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
