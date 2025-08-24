from typing import Tuple, Dict, Any
from django.utils import timezone
from ..models import Questionnaire, NotificationLog

class NotificationService:
    @staticmethod
    def notify_finder(q: Questionnaire) -> Tuple[bool, Dict[str, Any]]:
        payload = {
            "type": "QUESTIONNAIRE_DELIVERED",
            "questionnaire_id": str(q.id),
            "post_id": q.post_id,
            "finder_id": getattr(q.post, "user_id", None),
            "delivered_at": timezone.now().isoformat(),
        }
        ok = True  # 실제 연동 시 결과로 변경
        NotificationLog.objects.create(questionnaire=q, sent=ok, payload=payload)
        return ok, payload
