from django.db.models import F
from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from ..models import LostItem, CategoryCount
from ..serializers import LostItemResponseSerializer
from core.common.utils.responses import success_response
from ml.nlp.similarity import LostItemsRecommander
from ml.llm.gemini_text2json import parse_item_by_genai

@api_view(['GET'])
@permission_classes([AllowAny])
def lost_items_list(request):
    """분실물 목록 조회 API"""

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
@permission_classes([AllowAny])
def lost_items_list_by_search(request):
    """분실물 목록 검색 API"""

    # 1. 쿼리 파라미터 처리
    search_query = request.GET.get('search_query', 1)
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    status_filter = request.GET.get('status', None)

    # 2. 모든 분실물 필터링
    queryset = LostItem.objects.all().order_by('-created_at')

    # 3. 상태별 필터링 (선택사항)
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # 3-1. 검색어에 따른 추천된 습득물
    query = parse_item_by_genai(search_query)
    recs = LostItemsRecommander(queryset, query, top_k=queryset.count())

    # 3-2. 검색어에 따른 카테고리 검색 횟수 추가 
    category_key = query.split(" ")[0]
    obj, _ = CategoryCount.objects.get_or_create(category=category_key)
    obj.search_count = F("search_count") + 1
    obj.save(update_fields=["search_count"])
    obj.refresh_from_db()

    # 4. 페이징 처리
    paginator = Paginator(recs, limit)

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



