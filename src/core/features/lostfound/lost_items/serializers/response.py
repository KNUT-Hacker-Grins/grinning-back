# lost_items/serializers/response.py
from rest_framework import serializers
from ..models import LostItem
from django.contrib.auth import get_user_model # Import get_user_model

User = get_user_model() # Get the User model


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'profile_picture_url']


class LostItemResponseSerializer(serializers.ModelSerializer):
    """분실물 신고 응답용 시리얼라이저 (Refactored)"""
    user = OwnerSerializer(read_only=True)

    class Meta:
        model = LostItem
        fields = [
            'id',
            'user', # Use the nested OwnerSerializer
            'title',
            'description',
            'lost_at',
            'lost_location',
            'latitude',
            'longitude',
            'image_urls',
            'category',
            'reward',
            'status',
        ]
        read_only_fields = fields # Make all fields read-only for this response serializer

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        # Ensure image_urls is always a list
        if not isinstance(ret.get('image_urls'), list):
            ret['image_urls'] = []
        
        # Handle case where user might be null or has no profile picture
        if not ret.get('user'):
            ret['user'] = {
                'id': None,
                'email': '익명',
                'name': '익명',
                'profile_picture_url': '/default-profile.png'
            }
        elif not ret.get('user').get('profile_picture_url'):
            ret['user']['profile_picture_url'] = '/default-profile.png'

        # --- Final Debugging ---
        print(f"--- Final JSON for LostItem ID {instance.id}: {ret} ---")
        # --- End Final Debugging ---

        return ret