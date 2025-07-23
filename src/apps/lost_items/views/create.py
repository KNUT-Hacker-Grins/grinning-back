from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import LostItemCreateSerializer
from core.utils.responses import success_response, error_response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_lost_item(request):
    """분실물 신고 등록 API"""

    # 1. 요청 데이터 시리얼라이저로 검증
    serializer = LostItemCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(
            error="입력 데이터가 올바르지 않습니다.",
            code=400,
            details=serializer.errors
        )

    try:
        # 2. 분실물 신고 생성
        lost_item = serializer.save(user=request.user)

        # 3. 성공 응답
        return success_response(
            data={
                "id": str(lost_item.id),
                "title": lost_item.title,
                "status": lost_item.status
            },
            message="신고 완료",
            code=201
        )

    except Exception as e:
        return error_response(
            error="분실물 신고 등록 중 오류가 발생했습니다.",
            code=500
        )