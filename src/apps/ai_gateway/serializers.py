from rest_framework import serializers
from ml.vision.predictor import YOLOManager

class ClassificationSerializer(serializers.Serializer):
    image_url = serializers.URLField(help_text="분류할 이미지의 URL")
    
    category = serializers.JSONField(read_only=True)

    def create(self, validated_data):
        image_url = validated_data.get('image_url')
        prediction_list = YOLOManager().predict_yolo(image_url)
        return prediction_list
