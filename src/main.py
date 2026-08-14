#!/usr/bin/env python
import os
import sys
from pathlib import Path

def main():
    # main.py가 src/ 안으로 이동했으므로, 이 파일의 위치 자체가 src 디렉터리
    SRC_DIR = Path(__file__).resolve().parent

    # src를 모듈 경로에 추가해서 'core', 'apps' 등을 import 가능하게 함
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    # 👇 실제 settings 경로로 교체
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()

"""

python src/main.py startapp reports
python src/main.py makemigrations
python src/main.py migrate
python src/main.py createsuperuser
python src/main.py runserver
python src/main.py makemigrations accounts chat chatbot found_items lost_items reports lost_insight police

from apps.accounts.models import User
user_count = User.objects.count()
print(user_count)

"""