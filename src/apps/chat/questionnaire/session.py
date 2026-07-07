import uuid
from django.utils import timezone
from .models import QuestionSession

COOKIE_NAME = "chat_session_id"

def _ensure_session_by_id(session_id, state="INIT"):
    if not session_id:
        session_id = uuid.uuid4().hex[:16]
        return QuestionSession.objects.create(session_id=session_id, state=state)
    try:
        return QuestionSession.objects.get(session_id=session_id)
    except QuestionSession.DoesNotExist:
        return QuestionSession.objects.create(session_id=session_id, state=state)

def get_or_create_session_from_request(request):
    """
    요청에서 session_id를 쿠키 → 헤더 → 쿼리 → 바디 순으로 찾고,
    없으면 새로 만들고 반환. (created=True/False 함께 반환)
    """
    sid = (
        request.COOKIES.get(COOKIE_NAME)
        or request.headers.get("X-Chat-Session-Id")
        or request.GET.get("session_id")
        or (request.data.get("session_id") if hasattr(request, "data") else None)
    )
    session = _ensure_session_by_id(sid)
    created = (sid is None or sid != session.session_id)  # 새로 만든 경우
    # 핑 차원에서 갱신
    session.updated_at = timezone.now()
    session.save(update_fields=["updated_at"])
    return session, created