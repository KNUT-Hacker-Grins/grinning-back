from decouple import Csv, config

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default=(
        'http://localhost:3000,'
        'https://unit6frontdx-2swg.vercel.app,'
        'https://unit6-front.vercel.app'
    ),
    cast=Csv(),
)

ALLOWED_HOSTS = [
    "54.180.86.22",
    "cheetahsmiling.duckdns.org",
    ".render.com",
    "unit6-back-1.onrender.com", 
    "unit6frontdx-2swg.vercel.app", 
    "unit6-front.vercel.app", 
    "localhost",
    "127.0.0.1"
]
