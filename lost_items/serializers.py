from rest_framework import serializers
from .models import LostItem
from django.contrib.auth import get_user_model

User = get_user_model()


class LostItemCreateSerializer(serializers.ModelSerializer):
    """분실물 신고 등록용 시리얼라이저"""

    class Meta:
        model = LostItem
        fields = [
            'title',
            'description',
            'lost_at',
            'lost_location',
            'image_urls',
            'category',
            'reward'
        ]

    def create(self, validated_data):
        """분실물 신고 생성"""
        return LostItem.objects.create(**validated_data)


class LostItemResponseSerializer(serializers.ModelSerializer):
    """분실물 신고 응답용 Serializer"""

    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = LostItem
        fields = [
            'id',
            'title',
            'description',
            'lost_at',
            'lost_location',
            'image_urls',
            'category',
            'reward',
            'status',
            'user_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'status', 'user_name', 'created_at', 'updated_at']

class LostItemUpdateSerializer(serializers.ModelSerializer):
    """분실물 신고 수정용 시리얼라이저"""

    class Meta:
        model = LostItem
        fields = [
            'title',
            'description',
            'lost_at',
            'lost_location',
            'image_urls',
            'category',
            'reward'
        ]

    def update(self, instance, validated_data):
        """분실물 정보 업데이트"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance