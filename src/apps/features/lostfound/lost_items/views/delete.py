from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import LostItem
from apps.lost_items.utils.responses import success_response, error_response


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_lost_item(request, id):
    """분실물 삭제 API"""

    try:
        # 1. 분실물 조회
        lost_item = get_object_or_404(LostItem, id=id)

        # 2. 권한 확인
        if lost_item.user != request.user:
            return error_response(
                error="본인이 작성한 분실물만 삭제할 수 있습니다.",
                code=403
            )

        # 3. 분실물 삭제
        lost_item.delete()

        # 4. 성공 응답
        return success_response(
            message="삭제 완료"
        )

    except LostItem.DoesNotExist:
        return error_response(
            error="해당 분실물을 찾을 수 없습니다.",
            code=404
        )

    except Exception as e:
        return error_response(
            error="분실물 삭제 중 오류가 발생했습니다.",
            code=500
        )