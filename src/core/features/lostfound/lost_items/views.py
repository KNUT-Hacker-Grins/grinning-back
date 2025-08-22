from django.db.models import F
from django.utils import timezone
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import LostItem
from .serializers import (
    LostItemResponseSerializer, 
    LostItemCreateSerializer, 
    LostItemStatusSerializer,
    LostItemUpdateSerializer
)
from core.common.utils.responses import success_response, error_response
from core.integrations.lost_insight.models import CategoryDailyCount
from ml.nlp.similarity import LostItemsRecommander
from ml.llm.gemini import GeminiService


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_delete_lost_item(request, id):
    """관리자 분실물 신고 강제 삭제 API"""

    # 1. 분실물 조회 (없으면 404)
    lost_item = get_object_or_404(LostItem, id=id)

    # 2. 강제 삭제 (관리자 권한이므로 작성자 확인 불필요)
    lost_item.delete()

    # 3. 성공 응답
    return success_response(
        message="강제 삭제 완료",
        code=200
    )

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

@api_view(['POST'])
@permission_classes([AllowAny])
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
        user = request.user if getattr(request.user, "is_authenticated", False) else None
        lost_item = serializer.save(user=user) 
        
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
    

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_lost_item(request, id):
    """분실물 삭제 API"""

    try:
        # 1. 분실물 조회
        lost_item = get_object_or_404(LostItem, id=id)

        # # 2. 권한 확인
        # if lost_item.user != request.user:
        #     return error_response(
        #         error="본인이 작성한 분실물만 삭제할 수 있습니다.",
        #         code=403
        #     )

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
    search_query = request.GET.get('search_query', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    status_filter = request.GET.get('status', None)

    # 2. 모든 분실물 필터링
    queryset = LostItem.objects.all().order_by('-created_at')

    # 3. 상태별 필터링 (선택사항)
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # 3-1. 검색어에 따른 추천된 습득물
    query = GeminiService.call_gemini_for_parsing_text(search_query)
    recs = LostItemsRecommander(total_count=queryset.count()).analy_similarity_for_Tfidf(query=query)

    # 3-2. 검색어에 따른 카테고리 검색 횟수 추가 
    print(query)
    category_key = query.split(" ")[0]
    today = timezone.now().date()
    obj, _ = CategoryDailyCount.objects.get_or_create(category=category_key, date=today)
    obj.count = F("count") + 1
    obj.save(update_fields=["count"])
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
            "category_key": category_key,
            "page": page,
            "limit": limit,
            "total": paginator.count
        },
        message="분실물 목록 조회 성공"
    )

@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_lost_item_status(request, id):
    """분실물 상태 변경 API"""

    try:
        # 1. 분실물 조회
        lost_item = get_object_or_404(LostItem, id=id)

        # # 2. 권한 확인
        # if lost_item.user != request.user:
        #     return error_response(
        #         error="본인이 작성한 분실물만 상태 변경할 수 있습니다.",
        #         code=403
        #     )

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