from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = serializers.StringRelatedField(many=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'content', 'sender', 'timestamp', 'message_type']