from django.urls import path
from .views import social_login, google_callback, kakao_callback, login_password, register_user
from .views.profile import UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView # TokenBlacklistView 임포트

urlpatterns = [
    path('auth/login', social_login, name='social_login'),
    path('auth/login/password', login_password, name='login_password'),
    path('users/me', UserProfileView.as_view(), name='user_profile'),
    path('auth/google/callback', google_callback, name='google_callback'),
    path('auth/kakao/callback', kakao_callback, name='kakao_callback'),
    path('auth/register', register_user, name='register_user'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout', TokenBlacklistView.as_view(), name='token_blacklist'), # 명시적 로그아웃 URL 추가
]