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
            'title',
            'description',
            'lost_location',
            'image_urls',
            'category',
            'reward',
            'status',
            'owner'
        ]
        read_only_fields = ['id', 'status', 'owner']

    def get_owner(self, obj):
        return {
            "nickname": obj.user.name
        }