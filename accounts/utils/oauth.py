# accounts/utils/oauth.py
import requests
from django.conf import settings


class KakaoOAuth:
    @staticmethod
    def get_user_info(auth_code):
        """카카오 OAuth로 사용자 정보 가져오기"""
        # 1. 액세스 토큰 받기
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_CLIENT_ID,
            'client_secret': settings.KAKAO_CLIENT_SECRET,
            'code': auth_code,
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            raise Exception("카카오 액세스 토큰 요청 실패")

        # 2. 사용자 정보 받기
        user_url = "https://kapi.kakao.com/v2/user/me"
        headers = {'Authorization': f"Bearer {token_json['access_token']}"}

        user_response = requests.get(user_url, headers=headers)
        user_json = user_response.json()

        return {
            'social_id': str(user_json['id']),
            'email': user_json['kakao_account']['email'],
            'name': user_json['kakao_account']['profile']['nickname'],
            'provider': 'kakao'
        }


class GoogleOAuth:
    @staticmethod
    def get_user_info(auth_code):
        """구글 OAuth로 사용자 정보 가져오기"""
        # 1. 액세스 토큰 받기
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'code': auth_code,
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            raise Exception("구글 액세스 토큰 요청 실패")

        # 2. 사용자 정보 받기
        user_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f"Bearer {token_json['access_token']}"}

        user_response = requests.get(user_url, headers=headers)
        user_json = user_response.json()

        return {
            'social_id': user_json['id'],
            'email': user_json['email'],
            'name': user_json['name'],
            'provider': 'google'
        }