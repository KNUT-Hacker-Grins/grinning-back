from decouple import config

FRONTEND_BASE_URL = config('FRONTEND_BASE_URL', default='https://unit6-front.vercel.app')

