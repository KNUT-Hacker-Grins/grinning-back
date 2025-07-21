# lost_items/views.py
from datetime import datetime

from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import LostItem
from .serializers import LostItemCreateSerializer, LostItemResponseSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_lost_item(request):
    """
    분실물 신고 등록 API
    POST /api/lost-items
    """

    # 1. 요청 데이터 시리얼라이저로 검증
    serializer = LostItemCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "code": 400,
            "error": "입력 데이터가 올바르지 않습니다.",
            "details": serializer.errors,
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)


    try:
        # 2. 분실물 신고 생성 (user 자동 설정)
        lost_item = serializer.save(user=request.user)

        # 3. 응답용 시리얼라이저로 변환
        response_serializer = LostItemResponseSerializer(lost_item)

        # 4. 성공 응답 (API 명세서 형식에 맞춤)
        return Response({
            "status": "success",
            "code": 201,
            "data": {
                "id": str(lost_item.id),
                "title": lost_item.title,
                "status": lost_item.status
            },
            "message": "신고 완료",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        # 5. 서버 에러 처리
        return Response({
            "status": "error",
            "code": 500,
            "error": "분실물 신고 등록 중 오류가 발생했습니다.",
            "timestamp": datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_lost_items(request):
    """
    내 분실물 목록 조회 API
    GET /api/lost-items/my
    """

    # 1. 쿼리 파라미터 처리
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    status_filter = request.GET.get('status', None)  # searching, found, cancelled

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

    # 6. API 명세서에 맞는 응답
    return Response({
        "status": "success",
        "code": 200,
        "data": {
            "items": serializer.data,
            "page": page,
            "limit": limit,
            "total": paginator.count
        },
        "message": "조회 성공",
        "timestamp": datetime.now().isoformat()
    }, status=status.HTTP_200_OK)