from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from apps.lost_items.utils.responses import success_response, error_response
from ..utils import GoogleOAuth, KakaoOAuth
from ..serializers.response import LoginResponseSerializer

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def google_callback(request):
    """
    구글 OAuth 콜백 + JWT 토큰 발급 API
    GET /api/auth/google/callback?code=xxx
    """
    code = request.GET.get('code')
    if not code:
        return error_response(
            error="Authorization code가 없습니다.",
            code=400
        )

    try:
        # 1. Google OAuth로 사용자 정보 가져오기
        user_info = GoogleOAuth.get_user_info(code)

        # 2. 사용자 조회 또는 생성
        user, created = User.objects.get_or_create(
            social_id=user_info['social_id'],
            provider=user_info['provider'],
            defaults={
                'email': user_info['email'],
                'name': user_info['name'],
                'is_active': True
            }
        )

        # 3. 기존 사용자인 경우 정보 업데이트
        if not created:
            user.email = user_info['email']
            user.name = user_info['name']
            user.save()

        # 4. JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)  # 필요시 사용

        # 5. 응답 데이터 구성 (LoginResponseSerializer 기준)
        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user
        }

        # 6. 성공 응답
        return success_response(
            data=LoginResponseSerializer(response_data).data,
            message="Google 로그인 성공"
        )

    except Exception as e:
        return error_response(
            error=f"Google 로그인 실패: {str(e)}",
            code=400
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def kakao_callback(request):
    code = request.GET.get('code')
    if not code:
        return error_response(error="Authorization code가 없습니다.", code=400)

    try:
        user_info = KakaoOAuth.get_user_info(code)
        user, created = User.objects.get_or_create(
            social_id=user_info['social_id'],
            provider=user_info['provider'],
            defaults={
                'email': user_info['email'],
                'name': user_info['name'],
                'is_active': True
            }
        )
        if not created:
            user.email = user_info['email']
            user.name = user_info['name']
            user.save()
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
            message="Kakao 로그인 성공"
        )
    except Exception as e:
        return error_response(
            error=f"Kakao 로그인 실패: {str(e)}",
            code=400
        )