from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.common.utils.responses import success_response
from apps.features.lostfound.lost_items.models import LostItem
from apps.features.lostfound.lost_items.serializers import LostItemResponseSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def lost_items_list(request):
    """내 분실물 목록 조회 API"""
    """분실물 목록 조회 API
    """

    # 1. 쿼리 파라미터 처리
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    status_filter = request.GET.get('status', None)

    # 2. 모든 분실물 필터링
    queryset = LostItem.objects.all().order_by('-created_at')

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
        message="분실물 목록 조회 성공"
    )

@api_view(['GET'])
@permission_classes([AllowAny])  # 관리자만 조회하도록 하려면 IsAdminUser로 교체
def all_lost_items(request):
    """모든 분실물 일괄 조회 API"""

    # 1. 쿼리 파라미터 처리
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    status_filter = request.GET.get('status', None)

    # 2. 전체 분실물에서 필터링
    queryset = LostItem.objects.all().order_by('-created_at')

    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # 3. 페이징 처리
    paginator = Paginator(queryset, limit)

    if page > paginator.num_pages:
        page = paginator.num_pages if paginator.num_pages > 0 else 1

    page_obj = paginator.get_page(page)

    # 4. 시리얼라이저로 변환
    serializer = LostItemResponseSerializer(page_obj, many=True)

    # 5. 성공 응답
    return success_response(
        data={
            "items": serializer.data,
            "page": page,
            "limit": limit,
            "total": paginator.count
        },
        message="전체 분실물 조회 성공"
    )
