from django.urls import path
from .views import social_login, google_callback, kakao_callback, login_password, register_user
from .views.profile import UserProfileView # 클래스 뷰 임포트

urlpatterns = [
    path('auth/login', social_login, name='social_login'),
    path('auth/login/password', login_password, name='login_password'),
    path('users/me', UserProfileView.as_view(), name='user_profile'), # 클래스 뷰 연결
    path('auth/google/callback', google_callback, name='google_callback'),
    path('auth/kakao/callback', kakao_callback, name='kakao_callback'),
    path('auth/register', register_user, name='register_user'),
]