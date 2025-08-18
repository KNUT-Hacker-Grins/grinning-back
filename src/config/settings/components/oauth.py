from decouple import config

# OAuth 설정
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
GOOGLE_REDIRECT_URI = config('GOOGLE_REDIRECT_URI', default='https://unit6frontdx-2swg.vercel.app/api/auth/google/callback')
KAKAO_CLIENT_ID = config('KAKAO_CLIENT_ID', default='')
KAKAO_CLIENT_SECRET = config('KAKAO_CLIENT_SECRET', default='')
KAKAO_REDIRECT_URI = config('KAKAO_REDIRECT_URI', default='https://unit6frontdx-2swg.vercel.app/api/auth/kakao/callback')

FRONTEND_BASE_URL = config('FRONTEND_BASE_URL', default='https://unit6-front.vercel.app')



