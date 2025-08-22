from rest_framework import serializers
from .models import FoundItem
from core.common.error.error import ImageClassificationError 
from core.features.accounts.models import User
from ml.vision.predictor import YOLOManager

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['social_id', 'email', 'name'] 

class FoundItemSerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=7, required=False, allow_null=True)
    image_urls = serializers.JSONField(required=False, allow_null=True)
    found_date = serializers.DateTimeField(write_only=True, source='found_at')
    class Meta:
        model = FoundItem
        # user 제거함 
        fields = ['id', 'title', 'description', 'found_at', 'found_location', 'latitude', 'longitude', 'image_urls', 'category', 'status', 'created_at', 'updated_at', 'found_date', 'color']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'found_at']

    # def create(self, validated_data):
    #     image_urls = validated_data.get('image_urls')
    #     if image_urls and len(image_urls) > 0: # Check if image_urls is not empty
    #         try:
    #             # Use the first image URL for prediction
    #             data = YOLOManager().predict_yolo(image_urls[0])
    #             validated_data = data if data else []
    #         except ImageClassificationError as e:
    #             print(f"[이미지 분류 오류] {e}") # Log the error
    #             validated_data = [] # Set to empty dict on failure
    #     else:
    #         validated_data = [] # Default to empty dict if no image_urls
    #     return super().create(validated_data)
    
    # def update(self, instance, validated_data):
    #     image_url = validated_data.get('image_url', instance.image_url)  # 수정된 값 or 기존값
    #     if image_url != instance.image_url:
    #         category = predict_image(image_url)
    #         validated_data['category'] = category if category else 'unknown'
    #     return super().update(instance, validated_data)

class FoundItemDetailSerializer(serializers.ModelSerializer):
    user = OwnerSerializer()

    class Meta:
        model = FoundItem
        fields = ['id', 'title', 'user', 'description', 'found_at', 'found_location', 'latitude', 'longitude', 'category', 'image_urls']
