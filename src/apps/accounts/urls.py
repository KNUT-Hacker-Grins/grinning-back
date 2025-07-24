from django.urls import path
from .views import social_login, get_user_profile, google_callback, kakao_callback

urlpatterns = [
    path('auth/login', social_login, name='social_login'),     # POST /api/auth/login
    path('users/me', get_user_profile, name='get_user_profile'), # GET /api/users/me
    path('auth/google/callback', google_callback, name='google_callback'), #토큰 발급용 임시 코드
    path('auth/kakao/callback', kakao_callback, name='kakao_callback'),
]