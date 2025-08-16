# lost_items/serializers/request.py
from rest_framework import serializers
from ..models import LostItem


class LostItemCreateSerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=7, required=False, allow_null=True)
    """분실물 신고 등록용 시리얼라이저"""

    class Meta:
        model = LostItem
        fields = [
            'title',
            'description',
            'lost_at',
            'lost_location',
            'latitude',
            'longitude',
            'image_urls',
            'category',
            'reward'
        ]

    def create(self, validated_data):
        return LostItem.objects.create(**validated_data)


class LostItemUpdateSerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=7, required=False, allow_null=True)
    """분실물 신고 수정용 시리얼라이저"""

    class Meta:
        model = LostItem
        fields = [
            'title',
            'description',
            'lost_at',
            'lost_location',
            'latitude',
            'longitude',
            'image_urls',
            'category',
            'reward'
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LostItemStatusSerializer(serializers.ModelSerializer):
    """분실물 상태 변경용 시리얼라이저"""

    class Meta:
        model = LostItem
        fields = ['status']

    def validate_status(self, value):
        allowed_statuses = ['searching', 'found', 'cancelled']
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"상태는 {allowed_statuses} 중 하나여야 합니다.")
        return value