import os
from ..base import BASE_DIR

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # 추가
