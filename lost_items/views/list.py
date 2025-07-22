# lost_items/views/list.py
from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import LostItem
from ..serializers import LostItemResponseSerializer
from FindMyLostProject.utils.responses import success_response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_lost_items(request):
    """내 분실물 목록 조회 API"""

    # 1. 쿼리 파라미터 처리
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    status_filter = request.GET.get('status', None)

    # 2. 내 분실물만 필터링
    queryset = LostItem.objects.filter(user=request.user).order_by('-created_at')

    # 3. 상태별 필터링 (선택사항)
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # 4. 페이징 처리
    paginator = Paginator(queryset, limit)

    if page > paginator.num_pages:
        page = paginator.num_pages if paginator.num_pages > 0 else 1

    page_obj = paginator.get_page(page)

    # 5. 시리얼라이저로 변환
    serializer = LostItemResponseSerializer(page_obj, many=True)

    # 6. 성공 응답
    return success_response(
        data={
            "items": serializer.data,
            "page": page,
            "limit": limit,
            "total": paginator.count
        },
        message="조회 성공"
    )