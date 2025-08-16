from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from core.common.utils.permissions import IsAdminUser
from core.common.utils.responses import success_response
from core.features.lostfound.lost_items.models import LostItem
from core.features.lostfound.lost_items.serializers.response import LostItemResponseSerializer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_lost_items_list(request):
    """관리자 분실물 신고 일괄 조회 API"""

    # 1. 쿼리 파라미터 처리
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    status_filter = request.GET.get('status', None)
    reported = request.GET.get('reported', None)

    # 2. 모든 LostItem 조회
    queryset = LostItem.objects.all().order_by('-created_at')

    # 3. 상태별 필터링
    if status_filter and status_filter != 'all':
        queryset = queryset.filter(status=status_filter)

    # 4. 신고된 글 필터링 (reported=true일 때만)
    if reported == 'true':
        # TODO: Report 모델과 연결 필요
        pass

    # 5. 페이징 처리
    paginator = Paginator(queryset, limit)

    if page > paginator.num_pages:
        page = paginator.num_pages if paginator.num_pages > 0 else 1

    page_obj = paginator.get_page(page)

    # 6. 시리얼라이저로 변환
    serializer = LostItemResponseSerializer(page_obj, many=True)

    # 7. 성공 응답
    return success_response(
        data={
            "items": serializer.data,
            "page": page,
            "limit": limit,
            "total": paginator.count
        },
        message="조회 성공",
        code=201
    )