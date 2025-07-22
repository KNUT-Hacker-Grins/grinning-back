from rest_framework import serializers
from .ml.predictor import predict_image
from .models import FoundItem
from accounts.models import User

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['social_id', 'email', 'name'] 

class FoundItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoundItem
        fields = ['id', 'user', 'title', 'description', 'found_at', 'found_location', 'image_url', 'category', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'category']

    def create(self, validated_data):
        image_url = validated_data.get('image_url')
        category = predict_image(image_url)
        validated_data['category'] = category if category else 'unknown'
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        image_url = validated_data.get('image_url', instance.image_url)  # 수정된 값 or 기존값
        if image_url != instance.image_url:
            category = predict_image(image_url)
            validated_data['category'] = category if category else 'unknown'
        return super().update(instance, validated_data)

class FoundItemDetailSerializer(serializers.ModelSerializer):
    user = OwnerSerializer()

    class Meta:
        model = FoundItem
        fields = ['id', 'title', 'user', 'description', 'found_at', 'found_location', 'category', 'image_url']
