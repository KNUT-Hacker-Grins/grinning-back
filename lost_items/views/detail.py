# lost_items/views/detail.py
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import LostItem
from ..serializers import LostItemResponseSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def lost_item_detail(request, id):
    """분실물 상세 조회 API"""

    try:
        # 1. UUID로 분실물 조회
        lost_item = get_object_or_404(LostItem, id=id)

        # 2. 시리얼라이저로 변환
        serializer = LostItemResponseSerializer(lost_item)

        # 3. API 명세서에 맞는 응답
        return Response({
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "조회 성공",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_200_OK)

    except LostItem.DoesNotExist:
        return Response({
            "status": "error",
            "code": 404,
            "error": "해당 분실물을 찾을 수 없습니다.",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            "status": "error",
            "code": 500,
            "error": "분실물 조회 중 오류가 발생했습니다.",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)