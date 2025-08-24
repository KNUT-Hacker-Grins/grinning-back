# lost_items/serializers/response.py
from rest_framework import serializers
from ..models import LostItem
from django.contrib.auth import get_user_model # Import get_user_model

User = get_user_model() # Get the User model


class LostItemResponseSerializer(serializers.ModelSerializer):
    """분실물 신고 응답용 시리얼라이저"""

    user_profile_picture_url = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField() # Added this line

    class Meta:
        model = LostItem
        fields = [
            'id',
            'description',
            'lost_at',
            'lost_location',
            'latitude',
            'longitude',
            'image_urls',
            'category',
            'reward',
            'status',
            'user_profile_picture_url',
            'user_name', # Added this line
        ]
        read_only_fields = ['id', 'status', 'lost_at', 'lost_location', 'latitude', 'longitude', 'user_profile_picture_url', 'user_name'] # Added user_name

    def get_user_profile_picture_url(self, obj):
        if obj.user and obj.user.profile_picture_url:
            return obj.user.profile_picture_url
        return None # Or a default placeholder URL

    def get_user_name(self, obj): # Added this method
        if obj.user and hasattr(obj.user, 'name'):
            return obj.user.name
        return "익명" # Default to "익명" if user or user.name is not available

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        if not isinstance(ret.get('image_urls'), list):
            ret['image_urls'] = []
        
        return ret