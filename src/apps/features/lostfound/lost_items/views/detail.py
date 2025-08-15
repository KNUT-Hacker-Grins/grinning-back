from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from apps.common.utils.responses import success_response, error_response
from apps.features.lostfound.lost_items.models import LostItem
from apps.features.lostfound.lost_items.serializers import LostItemResponseSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def lost_item_detail(request, id):
    """분실물 상세 조회 API"""

    try:
        # 1. UUID로 분실물 조회
        lost_item = get_object_or_404(LostItem, id=id)

        # 2. 시리얼라이저로 변환
        serializer = LostItemResponseSerializer(lost_item)

        # 3. 성공 응답
        return success_response(
            data=serializer.data,
            message="조회 성공"
        )

    except LostItem.DoesNotExist:
        return error_response(
            error="해당 분실물을 찾을 수 없습니다.",
            code=404
        )

    except Exception as e:
        return error_response(
            error="분실물 조회 중 오류가 발생했습니다.",
            code=500
        )