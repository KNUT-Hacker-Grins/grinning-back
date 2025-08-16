import os
import uuid
from rest_framework import serializers
from django.core.files.storage import default_storage

class FileUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(write_only=True)
    
    # 응답으로 나갈 필드 정의
    image_url = serializers.CharField(read_only=True)

    def validate_image(self, image):
        # 파일 크기 검증 (5MB 제한)
        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            raise serializers.ValidationError("파일 크기는 5MB 이하여야 합니다.")

        # 파일 형식 검증
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if image.content_type not in allowed_types:
            raise serializers.ValidationError("jpg, png, webp 형식만 업로드 가능합니다.")
            
        return image

    def create(self, validated_data):
        image = validated_data.get('image')
        
        # 1. 고유한 파일명 생성
        file_extension = os.path.splitext(image.name)[1]
        unique_filename = f"uploads/{uuid.uuid4()}{file_extension}"
        
        # 2. 파일 저장 (S3)
        saved_path = default_storage.save(unique_filename, image)
        
        # 3. S3 URL 생성
        image_url = default_storage.url(saved_path)
        
        return {
            'image_url': image_url
        }
