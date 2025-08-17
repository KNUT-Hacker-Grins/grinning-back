import uuid
from ..models import ChatSession
from ..domain.state import ChatState

def _ensure_session(session_id: str = ""):
    if not session_id:
        session_id = uuid.uuid4().hex[:16]
        return ChatSession.objects.create(session_id=session_id, state=ChatState.IDLE.value)
    try:
        return ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return ChatSession.objects.create(session_id=session_id, state=ChatState.IDLE.value)
