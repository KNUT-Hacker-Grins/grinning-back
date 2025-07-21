# lost_items/views/update.py
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import LostItem
from ..serializers import LostItemUpdateSerializer


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_lost_item(request, id):
    """분실물 정보 수정 API"""

    try:
        # 1. 분실물 조회
        lost_item = get_object_or_404(LostItem, id=id)

        # 2. 권한 확인 (본인 게시글만 수정 가능)
        if lost_item.user != request.user:
            return Response({
                "status": "error",
                "code": 403,
                "error": "본인이 작성한 분실물만 수정할 수 있습니다.",
                "timestamp": datetime.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)

        # 3. 요청 데이터 검증
        serializer = LostItemUpdateSerializer(lost_item, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "code": 400,
                "error": "입력 데이터가 올바르지 않습니다.",
                "details": serializer.errors,
                "timestamp": datetime.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)

        # 4. 분실물 정보 업데이트
        updated_lost_item = serializer.save()

        # 5. API 명세서에 맞는 응답
        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "id": str(updated_lost_item.id),
                "title": updated_lost_item.title
            },
            "message": "수정 완료",
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
            "error": "분실물 수정 중 오류가 발생했습니다.",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)