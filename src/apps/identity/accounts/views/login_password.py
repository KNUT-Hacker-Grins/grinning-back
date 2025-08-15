from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from apps.common.utils.responses import error_response, success_response
from apps.identity.accounts.serializers.request import LoginPasswordRequestSerializer
from apps.identity.accounts.serializers.response import LoginResponseSerializer # 기존 로그인 응답 시리얼라이저 재사용

@api_view(['POST'])
@permission_classes([AllowAny])
def login_password(request):
    """
    이메일/비밀번호 기반 사용자 로그인 API
    POST /api/auth/login/password
    """
    serializer = LoginPasswordRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            error="로그인 정보가 올바르지 않습니다.",
            code=400,
            details=serializer.errors
        )

    try:
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user
        }

        return success_response(
            data=LoginResponseSerializer(response_data).data,
            message="로그인 성공"
        )
    except Exception as e:
        return error_response(
            error=f"로그인 중 오류가 발생했습니다: {str(e)}",
            code=500
        )
