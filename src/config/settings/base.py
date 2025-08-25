from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parents[3]
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

from .components.apps import *           
from .components.middleware import *     
from .components.database import *       
from .components.rest_jwt import *       
from .components.cors_csrf import *      
from .components.static_media import *   
from .components.auth import *            
from .components.logging import *        
from .components.celery import *         
from .components.gemini import *      
from .components.aws import *
from .components.etc import *
from .components.templates import *
from .components.rest_jwt import *
from .components.oauth import *

ROOT_URLCONF = "config.urls"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True
