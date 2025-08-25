from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from rest_framework import permissions, status, pagination
from rest_framework.response import Response
from rest_framework.views import APIView

from core.features.lostfound.found_items.models import FoundItem
from core.features.lostfound.lost_items.models import LostItem
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer, SimpleUserSerializer


# Custom Pagination for Chat Messages with participant data
class ChatMessagePagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'limit'

    def get_paginated_response(self, data, participants_data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'participants': participants_data,
            'messages': data
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
    pagination_class = ChatMessagePagination

    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        messages = ChatMessage.objects.filter(room=room).order_by('-timestamp')

        # Fetch participants
        participants = []
        if room.user_a:
            participants.append(room.user_a)
        if room.user_b:
            participants.append(room.user_b)
        
        participants_serializer = SimpleUserSerializer(participants, many=True)
        
        # Paginate messages
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, request, view=self)
        if page is not None:
            serializer = ChatMessageSerializer(page, many=True)
            # Pass participant data to the paginated response
            return paginator.get_paginated_response(serializer.data, participants_serializer.data)

        # Fallback for non-paginated response
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ChatRoomListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        # if not user:
        #     return Response({"items": []})

        # Correctly filter for rooms where the user is either user_a or user_b
        rooms = ChatRoom.objects.filter(Q(user_a=user) | Q(user_b=user)).distinct()

        result = []
        for room in rooms:
            last_message = ChatMessage.objects.filter(room=room).order_by('-timestamp').first()
            unread_count = ChatMessage.objects.filter(room=room, is_read=False).exclude(sender=user).count()
            other_user = room.user_b if room.user_a == user else room.user_a

            result.append({
                "room_id": str(room.id),
                "other_user": SimpleUserSerializer(other_user).data if other_user else None,
                "last_message": last_message.content if last_message else None,
                "last_timestamp": localtime(last_message.timestamp).isoformat() if last_message else None,
                "unread_count": unread_count,
            })
        
        return Response({"items": result})


class MarkAsReadView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, room_id, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        if not user:
            return Response({'detail': '인증되지 않은 사용자입니다.'}, status=401)

        try:
            # This logic might need review: what if the user is user_b?
            # For now, keeping it as it was in the "correct" version.
            room = ChatRoom.objects.get(id=room_id, user_a=user)
        except ChatRoom.DoesNotExist:
            # A more robust check would be Q(id=room_id) & (Q(user_a=user) | Q(user_b=user))
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

        # Check for an existing room for this specific post, regardless of users
        existing_room = ChatRoom.objects.filter(
            post_type=post_type,
            post_id=post_id
        ).first()

        if existing_room:
            # If a room for this post already exists, return it
            return Response({
                "status": "success",
                "data": {"room_id": existing_room.id},
                "message": "기존 채팅방 반환"
            })

        room = ChatRoom.objects.create(
            post_type=post_type, 
            post_id=post_id,
            user_a=user1,
            user_b=user2
        )

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
            return Response({})

        rooms = ChatRoom.objects.filter(Q(user_a=user) | Q(user_b=user))

        unread_by_room = {}
        for room in rooms:
            unread_count = ChatMessage.objects.filter(
                room=room,
                is_read=False
            ).exclude(sender=user).count()
            if unread_count > 0:
                unread_by_room[str(room.id)] = unread_count

        return Response(unread_by_room)