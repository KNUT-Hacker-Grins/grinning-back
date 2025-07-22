from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import UserResponseSerializer
from FindMyLostProject.utils.responses import success_response, error_response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    내 정보 조회 API
    GET /api/users/me
    """

    try:
        # 1. JWT에서 사용자 정보 가져오기
        user = request.user

        # 2. 시리얼라이저로 변환
        serializer = UserResponseSerializer(user)

        # 3. 성공 응답
        return success_response(
            data=serializer.data,
            message="조회 성공"
        )

    except Exception as e:
        return error_response(
            error="사용자 정보 조회 중 오류가 발생했습니다.",
            code=500
        )