from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.common.utils.responses import success_response, error_response
from apps.features.lostfound.lost_items.models import LostItem
from apps.features.lostfound.lost_items.serializers import LostItemUpdateSerializer

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_lost_item(request, id):
    """분실물 정보 수정 API"""

    try:
        # 1. 분실물 조회
        lost_item = get_object_or_404(LostItem, id=id)

        # 2. 권한 확인
        if lost_item.user != request.user:
            return error_response(
                error="본인이 작성한 분실물만 수정할 수 있습니다.",
                code=403
            )

        # 3. 요청 데이터 검증
        serializer = LostItemUpdateSerializer(lost_item, data=request.data, partial=True)

        if not serializer.is_valid():
            return error_response(
                error="입력 데이터가 올바르지 않습니다.",
                code=400,
                details=serializer.errors
            )

        # 4. 분실물 정보 업데이트
        updated_lost_item = serializer.save()

        # 5. 성공 응답
        return success_response(
            data={
                "id": str(updated_lost_item.id),
                "title": updated_lost_item.title
            },
            message="수정 완료"
        )

    except LostItem.DoesNotExist:
        return error_response(
            error="해당 분실물을 찾을 수 없습니다.",
            code=404
        )

    except Exception as e:
        return error_response(
            error="분실물 수정 중 오류가 발생했습니다.",
            code=500
        )