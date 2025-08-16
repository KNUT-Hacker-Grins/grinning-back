# lost_items/serializers/response.py
from rest_framework import serializers
from ..models import LostItem


class LostItemResponseSerializer(serializers.ModelSerializer):
    """분실물 신고 응답용 시리얼라이저"""

    owner = serializers.SerializerMethodField()

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
            'owner'
        ]
        read_only_fields = ['id', 'status', 'owner', 'lost_at', 'lost_location', 'latitude', 'longitude']

    def get_owner(self, obj):
        user_name = obj.user.name if obj.user else None
        return {
            "nickname": user_name
        }

    def to_representation(self, instance):
        # Get the default representation
        ret = super().to_representation(instance)
        
        # Ensure image_urls is always a list
        if not isinstance(ret.get('image_urls'), list):
            ret['image_urls'] = []
        
        return ret