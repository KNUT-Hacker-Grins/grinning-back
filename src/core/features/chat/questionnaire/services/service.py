from django.utils import timezone
from ..models import ChatSession, ChatState
from ..utils import push_step
from ..models import Questionnaire
from ..services.notification import NotificationService

def handle_user_input(session: ChatSession, text: str, maybe_post_id: int | None = None):
    """
    사용자가 보낸 입력(text)을 현재 state에 맞게 처리.
    최초 요청에서 post_id가 함께 오면 세션에 저장해 둡니다.
    """
    # post_id 세팅(최초 1회)
    if maybe_post_id and not session.post_id:
        session.post_id = maybe_post_id
        session.save(update_fields=["post_id"])

    state = session.state

    if state == ChatState.INIT:
        push_step(session.session_id, "bot", "어떤 물건을 잃어버리셨나요? 상세히 물건 설명을 입력해주세요.")
        session.state = ChatState.ASK_DESC
        session.save(update_fields=["state"])
        return

    if state == ChatState.ASK_DESC:
        session.lost_desc = text.strip()
        session.state = ChatState.ASK_PLACE
        session.save(update_fields=["lost_desc", "state"])
        push_step(session.session_id, "bot", "어디서 물건을 잃어버리셨나요?")
        return

    if state == ChatState.ASK_PLACE:
        session.lost_place = text.strip()
        session.state = ChatState.ASK_TIME
        session.save(update_fields=["lost_place", "state"])
        push_step(session.session_id, "bot", "언제 물건을 잃어버리셨나요?")
        return

    if state == ChatState.ASK_TIME:
        session.lost_time = text.strip()
        session.state = ChatState.DONE
        session.save(update_fields=["lost_time", "state"])

        # 요약 보여주기
        summary = f"- 물건: {session.lost_desc}\n- 장소: {session.lost_place}\n- 시점: {session.lost_time}"
        push_step(session.session_id, "system", "아래 내용으로 습득자에게 전달합니다.")
        push_step(session.session_id, "bot", summary)

        # 필수 값 확인
        if not session.post_id:
            push_step(session.session_id, "system",
                      "오류: 연결된 습득글(post_id)이 없습니다. 처음 메시지에 post_id를 포함해 주세요.",
                      data={"error": "MISSING_POST_ID"})
            return

        q = Questionnaire.objects.create(
            session_id=session.session_id,
            post_id=session.post_id,
            status=Questionnaire.Status.PENDING,
            delivered_at=timezone.now(),
        )
        ok, _ = NotificationService.notify_finder(q)
        if ok:
            push_step(session.session_id, "bot", "습득자에게 질문지를 전달했어요. 승인/답변을 기다려주세요.",
                      data={"questionnaire_id": str(q.id), "notification_sent": True})
        else:
            push_step(session.session_id, "bot", "알림 전송 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
                      data={"questionnaire_id": str(q.id), "notification_sent": False})
        return

    if state == ChatState.DONE:
        # 이미 완료된 세션
        push_step(session.session_id, "system", "이미 질문을 모두 받았습니다. 새로 시작하려면 세션을 초기화하세요.")
        return