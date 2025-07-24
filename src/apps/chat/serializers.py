from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from django.contrib.auth import get_user_model
from apps.accounts.serializers.simple_user import SimpleUserSerializer

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = SimpleUserSerializer(many=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'participants']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'content', 'sender', 'timestamp', 'message_type']