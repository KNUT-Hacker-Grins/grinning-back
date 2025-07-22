from django.urls import path
from .views import social_login, get_user_profile

urlpatterns = [
    path('auth/login', social_login, name='social_login'),     # POST /api/auth/login
    path('users/me', get_user_profile, name='get_user_profile'), # GET /api/users/me
]