from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from ..models import User
from ..serializers import LoginRequestSerializer, LoginResponseSerializer
from ..utils import KakaoOAuth, GoogleOAuth
from lost_items.utils.responses import success_response, error_response

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def social_login(request):
    """
    소셜 로그인 API
    POST /api/auth/login
    """

    # 1. 요청 데이터 검증
    serializer = LoginRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(
            error="입력 데이터가 올바르지 않습니다.",
            code=400,
            details=serializer.errors
        )

    provider = serializer.validated_data['provider']
    auth_code = serializer.validated_data['code']

    try:
        # 2. OAuth로 사용자 정보 가져오기
        if provider == 'kakao':
            user_info = KakaoOAuth.get_user_info(auth_code)
        elif provider == 'google':
            user_info = GoogleOAuth.get_user_info(auth_code)
        else:
            return error_response(
                error="지원하지 않는 소셜 로그인 제공자입니다.",
                code=400
            )

        # 3. 사용자 조회 또는 생성
        user, created = User.objects.get_or_create(
            social_id=user_info['social_id'],
            provider=user_info['provider'],
            defaults={
                'email': user_info['email'],
                'name': user_info['name'],
                'is_active': True
            }
        )

        # 4. 기존 사용자인 경우 정보 업데이트
        if not created:
            user.email = user_info['email']
            user.name = user_info['name']
            user.save()

        # 5. JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # 6. 응답 데이터 구성
        response_data = {
            'access_token': access_token,
            'user': user
        }

        # 7. 성공 응답
        return success_response(
            data=LoginResponseSerializer(response_data).data,
            message="로그인 성공"
        )

    except Exception as e:
        return error_response(
            error=f"소셜 로그인 중 오류가 발생했습니다: {str(e)}",
            code=500
        )