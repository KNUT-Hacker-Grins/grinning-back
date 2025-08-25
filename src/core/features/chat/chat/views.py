from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, pagination
from rest_framework import permissions
from .models import ChatRoom
from .serializers import ChatRoomSerializer
from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer
from core.features.lostfound.found_items.models import FoundItem
from core.features.lostfound.lost_items.models import LostItem

class ChatMessageCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user if request.user.is_authenticated else None
            message = serializer.save(sender=user, room=room)
            return Response({
                'status': 'success',
                'code': 201,
                'data': ChatMessageSerializer(message).data,
                'message': '전송 완료'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatMessagePagination(pagination.PageNumberPagination):
    page_size = 20  # 원하는 기본 페이지 크기
    page_size_query_param = 'limit'

class ChatMessageListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        # if request.user not in room.participants.all():
        #     return Response({"detail": "접근 권한 없음"}, status=403)

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

from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, pagination
from rest_framework import permissions
from .models import ChatRoom
from .serializers import ChatRoomSerializer
from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer
from core.features.lostfound.found_items.models import FoundItem
from core.features.lostfound.lost_items.models import LostItem

# Custom Pagination for Chat Messages
class ChatMessagePagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'messages': data  # Use 'messages' key as expected by frontend
        })

class ChatMessageCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user if request.user.is_authenticated else None
            message = serializer.save(sender=user, room=room)
            return Response({
                'status': 'success',
                'code': 201,
                'data': ChatMessageSerializer(message).data,
                'message': '전송 완료'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatMessageListView(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = ChatMessagePagination  # Apply custom pagination

    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        messages = ChatMessage.objects.filter(room=room).order_by('-timestamp')
        
        # Standard pagination logic
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, request, view=self)
        if page is not None:
            serializer = ChatMessageSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Fallback for non-paginated response (if needed)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ChatRoomListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        # Assuming user can be null for anonymous access, adjust if needed
        if not user:
            return Response({"items": []}) # Return empty for anonymous

        rooms = ChatRoom.objects.filter(user_a=user).distinct()

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

            other_user = room.user_b
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
        
        # Wrap the result in a dictionary with 'items' key
        return Response({"items": result})


class MarkAsReadView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, room_id, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        if not user:
            return Response({'detail': '인증되지 않은 사용자입니다.'}, status=401)

        try:
            room = ChatRoom.objects.get(id=room_id, user_a=user)
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
    
class StartChatView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        post_id = request.data.get("post_id")
        post_type = request.data.get("post_type")

        if post_type not in ["found", "lost"]:
            return Response({"status": "error", "message": "유효하지 않은 post_type"}, status=400)

        PostModel = FoundItem if post_type == "found" else LostItem
        post = get_object_or_404(PostModel, id=post_id)
        
        user1 = request.user if request.user.is_authenticated else None
        if not user1:
            return Response({"status": "error", "message": "인증이 필요합니다."}, status=401)

        if user1 == post.user:
            return Response(
                {"status": "fail", "message": "자신의 글에는 채팅을 시작할 수 없습니다."},
                status=403
            )

        user2 = post.user

        # Find existing room between these two users for this post
        existing = ChatRoom.objects.filter(
            post_type=post_type,
            post_id=post_id,
            user_a=user1,
            user_b=user2
        ).first()
    
        if existing:
            serializer = ChatRoomSerializer(existing)
            return Response({
                "status": "success",
                "data": {"room_id": existing.id},
                "message": "기존 채팅방 반환"
            })

        # Create new room
        room = ChatRoom.objects.create(
            post_type=post_type, 
            post_id=post_id,
            user_a=user1,
            user_b=user2
        )

        serializer = ChatRoomSerializer(room)
        return Response({
            "status": "success",
            "data": {"room_id": str(room.id)},
            "message": "채팅방 생성 완료"
        }, status=201)

class UnreadCountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        if not user:
            return Response({}) # Return empty for anonymous

        rooms = ChatRoom.objects.filter(user_a=user)

        unread_by_room = {}
        for room in rooms:
            unread_count = ChatMessage.objects.filter(
                room=room,
                is_read=False
            ).exclude(sender=user).count()
            if unread_count > 0:
                unread_by_room[str(room.id)] = unread_count

        return Response(unread_by_room)



class MarkAsReadView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, room_id, *args, **kwargs):
        # user = request.user
        user = request.user if request.user.is_authenticated else None

        try:
            room = ChatRoom.objects.get(id=room_id, user_a=user)
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
    
class StartChatView(APIView):
    permission_classes = [permissions.AllowAny]

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
                    "user_a": serializer.data["user_a"],
                    "user_b": serializer.data["user_b"]
                },
                "message": "기존 채팅방 반환"
            })

        # 3. 새 채팅방 생성
        # if request.user == post.user:
        #     return Response(
        #         {
        #             "status": "fail",
        #             "code": 403,
        #             "message": "자신의 글에는 채팅을 시작할 수 없습니다."
        #         },
        #         status=403
        #     )
        
        room = ChatRoom.objects.create(post_type=post_type, post_id=post_id)
        user1 = request.user if request.user.is_authenticated else None
        user2 = post.user if post.user else None
        room = ChatRoom.objects.create(
            user_a=user1,
            user_b=user2
        )

        serializer = ChatRoomSerializer(room)
        return Response({
            "status": "success",
            "code": 201,
            "data": {
                "room_id": str(room.id),
                "user_a": serializer.data["user_a"],
                "user_b": serializer.data["user_b"]
            },
            "message": "채팅방 생성 완료"
        }, status=201)

class UnreadCountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # user = request.user
        user = request.user if request.user.is_authenticated else None
        rooms = ChatRoom.objects.filter(user_a=user)

        unread_by_room = {}
        for room in rooms:
            unread_count = ChatMessage.objects.filter(
                room=room,
                is_read=False
            ).exclude(sender=user).count()  # 내가 보낸 건 제외해야 진짜 '수신 안읽음'
            if unread_count > 0:
                unread_by_room[str(room.id)] = unread_count

        return Response(unread_by_room)
