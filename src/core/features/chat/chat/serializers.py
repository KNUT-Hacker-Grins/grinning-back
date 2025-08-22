from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from django.contrib.auth import get_user_model
from core.features.accounts.serializers.simple_user import SimpleUserSerializer

class ChatRoomSerializer(serializers.ModelSerializer):
    user_a = SimpleUserSerializer(read_only=True) 
    user_b = SimpleUserSerializer(read_only=True) 

    class Meta:
        model = ChatRoom
        fields = ['id', 'user_a', 'user_b']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'content', 'sender', 'timestamp', 'message_type']