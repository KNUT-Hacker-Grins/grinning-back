from rest_framework import serializers
from classifier.predictor import predict_image
from .models import FoundItem
from ..accounts.models import User

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
        fields = ['id', 'user', 'title', 'description', 'found_at', 'found_location', 'latitude', 'longitude', 'image_urls', 'category', 'status', 'created_at', 'updated_at', 'found_date']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'status', 'found_at', 'found_location']

    def create(self, validated_data):
        image_urls = validated_data.get('image_urls')
        if image_urls and len(image_urls) > 0: # Check if image_urls is not empty
            try:
                # Use the first image URL for prediction
                category = predict_image(image_urls[0])
                validated_data['category'] = category if category else {}
            except ImageClassificationError as e:
                print(f"[이미지 분류 오류] {e}") # Log the error
                validated_data['category'] = {} # Set to empty dict on failure
        else:
            validated_data['category'] = {} # Default to empty dict if no image_urls
        return super().create(validated_data)
    
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
        fields = ['id', 'title', 'user', 'description', 'found_at', 'found_location', 'latitude', 'longitude', 'category', 'image_url']
