from decouple import config
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'), # Render 환경 변수 사용
        conn_max_age=600
    )
}
