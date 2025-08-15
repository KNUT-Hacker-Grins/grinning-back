from rest_framework import serializers
from .services.predictor import predict_yolo

class ClassificationSerializer(serializers.Serializer):
    image_url = serializers.URLField(help_text="분류할 이미지의 URL")
    
    category = serializers.JSONField(read_only=True)

    def create(self, validated_data):
        image_url = validated_data.get('image_url')
        
        # 이미지 분류
        prediction_list = predict_yolo(image_url)
        
        return prediction_list
