import logging 
from config import settings
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from core.common.utils.responses import error_response
from core.features.accounts.utils import GoogleOAuth, KakaoOAuth

User = get_user_model()

# 로거 설정
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def google_callback(request):
    """
    구글 OAuth 콜백 + JWT 토큰 발급 및 프론트엔드 리디렉션
    GET /api/auth/google/callback?code=xxx
    """
    code = request.GET.get('code')
    if not code:
        logger.error("Google OAuth: Authorization code가 없습니다.")
        return error_response(
            error="인증 코드가 없습니다.", # 사용자에게는 일반적인 메시지
            code=400
        )

    try:
        user_info = GoogleOAuth.get_user_info(code)
        user, created = User.objects.get_or_create(
            social_id=user_info['social_id'],
            provider=user_info['provider'],
            defaults={
                'email': user_info['email'],
                'name': user_info['name'],
                'is_active': True,
                'profile_picture_url': user_info.get('profile_picture_url')
            }
        )
        if not created:
            user.email = user_info['email']
            user.name = user_info['name']
            user.profile_picture_url = user_info.get('profile_picture_url')
            user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        base_url = 'https://unit6-front.vercel.app/login/callback'
        query_params = urlencode({'access': access_token, 'refresh': refresh_token})
        redirect_url = f'{base_url}?{query_params}'

        return redirect(redirect_url)

        # return JsonResponse({
        #     "access": access_token,
        #     "refresh": refresh_token,
        #     "user": {
        #         "id": user.social_id,
        #         "email": user.email,
        #         "name": user.name,
        #         "provider": user_info["provider"]
        #     }
        # })

    except Exception as e:
        logger.exception(f"Google 로그인 실패: {e}") # 상세 에러 로깅
        error_message = urlencode({"message": "Google 로그인 중 오류가 발생했습니다. 다시 시도해주세요."})
        error_redirect_url = f'{settings.FRONTEND_BASE_URL}/login?error={error_message}'
        return redirect(error_redirect_url)


@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def kakao_callback(request):
    """
    카카오 OAuth 콜백 + JWT 토큰 발급 및 프론트엔드 리디렉션
    GET /api/auth/kakao/callback?code=xxx
    """
    code = request.GET.get('code')
    if not code:
        logger.error("Kakao OAuth: Authorization code가 없습니다.")
        return error_response(
            error="인증 코드가 없습니다.", # 사용자에게는 일반적인 메시지
            code=400
        )

    try:
        user_info = KakaoOAuth.get_user_info(code)
        user, created = User.objects.get_or_create(
            social_id=user_info['social_id'],
            provider=user_info['provider'],
            defaults={
                'email': user_info['email'],
                'name': user_info['name'],
                'is_active': True,
                'profile_picture_url': user_info.get('profile_picture_url')
            }
        )
        if not created:
            user.email = user_info['email']
            user.name = user_info['name']
            user.profile_picture_url = user_info.get('profile_picture_url') # 추가
            user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        base_url = 'https://unit6-front.vercel.app/login/callback'
        query_params = urlencode({'access': access_token, 'refresh': refresh_token})
        redirect_url = f'{base_url}?{query_params}'

        return redirect(redirect_url)

    except Exception as e:
        logger.exception(f"Kakao 로그인 실패: {e}") # 상세 에러 로깅
        error_message = urlencode({"message": "Kakao 로그인 중 오류가 발생했습니다. 다시 시도해주세요."})
        error_redirect_url = f'{settings.FRONTEND_BASE_URL}/login?error={error_message}'
        return redirect(error_redirect_url)