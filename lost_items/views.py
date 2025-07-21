# lost_items/views.py
from datetime import datetime
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

    # # lost_items/views.py
    # from datetime import datetime
    # from rest_framework.decorators import api_view, permission_classes
    # from rest_framework.permissions import AllowAny  # 추가
    # from rest_framework.response import Response
    # from rest_framework import status
    # from django.contrib.auth import get_user_model  # 추가
    # from .models import LostItem
    # from .serializers import LostItemCreateSerializer, LostItemResponseSerializer
    #
    # User = get_user_model()  # 추가
    #
    # @api_view(['POST'])
    # @permission_classes([AllowAny])  # 명시적으로 모든 사용자 허용
    # def create_lost_item(request):
    #     """분실물 신고 등록 API"""
    #
    #     # 1. 요청 데이터 시리얼라이저로 검증
    #     serializer = LostItemCreateSerializer(data=request.data)
    #
    #     if not serializer.is_valid():
    #         return Response({
    #             "status": "error",
    #             "code": 400,
    #             "error": "입력 데이터가 올바르지 않습니다.",
    #             "details": serializer.errors,
    #             "timestamp": datetime.now().isoformat()
    #         }, status=status.HTTP_400_BAD_REQUEST)
    #
    #     try:
    #         # 2. 임시 사용자 처리 (JWT 개발 전까지)
    #         if request.user.is_authenticated:
    #             user = request.user
    #         else:
    #             # 첫 번째 사용자를 임시로 사용
    #             user = User.objects.first()
    #             if not user:
    #                 return Response({
    #                     "status": "error",
    #                     "code": 400,
    #                     "error": "시스템에 사용자가 없습니다. 관리자에게 문의하세요.",
    #                     "timestamp": datetime.now().isoformat()
    #                 }, status=status.HTTP_400_BAD_REQUEST)
    #
    #         # 3. 분실물 신고 생성
    #         lost_item = serializer.save(user=user)
    #
    #         # 4. 성공 응답
    #         return Response({
    #             "status": "success",
    #             "code": 201,
    #             "data": {
    #                 "id": str(lost_item.id),
    #                 "title": lost_item.title,
    #                 "status": lost_item.status
    #             },
    #             "message": "신고 완료",
    #             "timestamp": datetime.now().isoformat()
    #         }, status=status.HTTP_201_CREATED)
    #
    #     except Exception as e:
    #         return Response({
    #             "status": "error",
    #             "code": 500,
    #             "error": f"분실물 신고 등록 중 오류: {str(e)}",
    #             "timestamp": datetime.now().isoformat()
    #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)