from django.shortcuts import redirect
from urllib.parse import urlencode
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from apps.lost_items.utils.responses import error_response
from ..utils import GoogleOAuth, KakaoOAuth
from ..serializers.response import LoginResponseSerializer

User = get_user_model()


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
        refresh_token = str(refresh)

        # 5. 프론트엔드 콜백 URL로 리디렉션
        base_url = 'http://localhost:3000/auth/callback'
        query_params = urlencode({'access': access_token, 'refresh': refresh_token})
        redirect_url = f'{base_url}?{query_params}'

        return redirect(redirect_url)

    except Exception as e:
        # 에러 발생 시 로그인 페이지로 리디렉션 또는 에러 페이지 표시
        error_message = urlencode({"message": f"Google 로그인 실패: {str(e)}"})
        error_redirect_url = f'http://localhost:3000/login?error={error_message}'
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

        # 프론트엔드 콜백 URL로 리디렉션
        base_url = 'http://localhost:3000/auth/callback'
        query_params = urlencode({'access': access_token, 'refresh': refresh_token})
        redirect_url = f'{base_url}?{query_params}'

        return redirect(redirect_url)

    except Exception as e:
        # 에러 발생 시 로그인 페이지로 리디렉션 또는 에러 페이지 표시
        error_message = urlencode({"message": f"Kakao 로그인 실패: {str(e)}"})
        error_redirect_url = f'http://localhost:3000/login?error={error_message}'
        return redirect(error_redirect_url)
