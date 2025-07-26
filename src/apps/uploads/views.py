from django.shortcuts import render

# Create your views here.
# uploads/views.py
import os
import uuid
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# 디버깅을 위한 로깅 추가
import logging
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """
    이미지 업로드 API
    - POST /api/upload/image
    - Form Data: image (파일)
    """

    # 1. 이미지 파일 존재 확인
    if 'image' not in request.FILES:
        return Response({
            "status": "error",
            "code": 400,
            "error": "이미지 파일이 필요합니다.",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)

    image_file = request.FILES['image']

    # 2. 파일 크기 검증 (5MB 제한)
    max_size = 5 * 1024 * 1024  # 5MB
    if image_file.size > max_size:
        return Response({
            "status": "error",
            "code": 400,
            "error": "파일 크기는 5MB 이하여야 합니다.",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)

    # 3. 파일 형식 검증
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if image_file.content_type not in allowed_types:
        return Response({
            "status": "error",
            "code": 400,
            "error": "jpg, png, webp 형식만 업로드 가능합니다.",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 4. 고유한 파일명 생성
        file_extension = os.path.splitext(image_file.name)[1]  # .jpg, .png 등
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # 5. 파일 저장 (uploads/ 폴더에)
        # default_storage.save()는 settings.py의 DEFAULT_FILE_STORAGE 설정에 따라 동작
        file_path = default_storage.save(f'uploads/{unique_filename}', image_file)

        # 6. 전체 URL 생성
        file_url = default_storage.url(file_path)
        full_url = request.build_absolute_uri(file_url)

        # 7. 성공 응답
        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "image_url": full_url
            },
            "message": "업로드 완료",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        # 8. 에러 처리 및 디버깅 정보 추가
        logger.exception("파일 업로드 중 예외 발생:") # 서버 로그에 상세 스택 트레이스 기록
        error_detail = f"--- {type(e).__name__}: {str(e)} ---" # 에러 타입과 메시지
        return Response({
            "status": "error",
            "code": 500,
            "error": f"파일 업로드 중 오류가 발생했습니다. {error_detail}", # 디버깅 정보 포함
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)