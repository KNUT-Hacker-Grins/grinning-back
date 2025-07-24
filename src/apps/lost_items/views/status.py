from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import LostItem
from ..serializers import LostItemStatusSerializer
from apps.lost_items.utils.responses import success_response, error_response


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_lost_item_status(request, id):
    """분실물 상태 변경 API"""

    try:
        # 1. 분실물 조회
        lost_item = get_object_or_404(LostItem, id=id)

        # 2. 권한 확인
        if lost_item.user != request.user:
            return error_response(
                error="본인이 작성한 분실물만 상태 변경할 수 있습니다.",
                code=403
            )

        # 3. 요청 데이터 검증
        serializer = LostItemStatusSerializer(lost_item, data=request.data, partial=True)

        if not serializer.is_valid():
            return error_response(
                error="입력 데이터가 올바르지 않습니다.",
                code=400,
                details=serializer.errors
            )

        # 4. 상태 변경
        updated_lost_item = serializer.save()

        # 5. 성공 응답
        return success_response(
            data={
                "id": str(updated_lost_item.id),
                "status": updated_lost_item.status
            },
            message="상태 변경 완료"
        )

    except LostItem.DoesNotExist:
        return error_response(
            error="해당 분실물을 찾을 수 없습니다.",
            code=404
        )

    except Exception as e:
        return error_response(
            error="분실물 상태 변경 중 오류가 발생했습니다.",
            code=500
        )