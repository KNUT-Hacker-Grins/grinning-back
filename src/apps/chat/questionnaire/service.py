from django.utils import timezone
from .models import QuestionSession, QuestionState
from .models import Questionnaire
from .notification import NotificationService

def build_response(session_id, state, reply, data=None):
    if data is None:
        data = {}

    return {
        "session_id": session_id,
        "state": state,
        "reply": reply,
        "data": data
    }

def handle_user_input(session: QuestionSession, text: str, maybe_post_id: int | None = None):
    """
    사용자가 보낸 입력(text)을 현재 state에 맞게 처리.
    최초 요청에서 post_id가 함께 오면 세션에 저장해 둡니다.
    """
    # post_id 세팅(최초 1회)
    if maybe_post_id and not session.post_id:
        session.post_id = maybe_post_id
        session.save(update_fields=["post_id"])

    state = session.state

    if state == QuestionState.INIT:
        response = build_response(session.session_id, state, "어떤 물건을 잃어버리셨나요? 상세히 물건 설명을 입력해주세요.")
        session.state = QuestionState.ASK_DESC
        session.save(update_fields=["state"])
        return response

    if state == QuestionState.ASK_DESC:
        session.lost_desc = text.strip()
        session.state = QuestionState.ASK_PLACE
        session.save(update_fields=["lost_desc", "state"])
        response = build_response(session.session_id, state, "어디서 물건을 잃어버리셨나요?")
        return response

    if state == QuestionState.ASK_PLACE:
        session.lost_place = text.strip()
        session.state = QuestionState.ASK_TIME
        session.save(update_fields=["lost_place", "state"])
        response = build_response(session.session_id, state, "언제 물건을 잃어버리셨나요?")
        return response

    if state == QuestionState.ASK_TIME:
        session.lost_time = text.strip()
        session.state = QuestionState.DONE
        session.save(update_fields=["lost_time", "state"])

        # 요약 보여주기
        summary = {
            "summary": f"아래 내용으로 습득자에게 전달합니다.\n- 물건: {session.lost_desc}\n- 장소: {session.lost_place}\n- 시점: {session.lost_time}"
            }
        
        response = build_response(session.session_id, state, summary)

        # 필수 값 확인
        if not session.post_id:
            response = build_response(session.session_id, state,
                      "오류: 연결된 습득글(post_id)이 없습니다. 처음 메시지에 post_id를 포함해 주세요.",
                      data={"error": "MISSING_POST_ID"})
            return response

        q = Questionnaire.objects.create(
            session_id=session.session_id,
            post_id=session.post_id,
            status=Questionnaire.Status.PENDING,
            delivered_at=timezone.now(),
        )
        ok, _ = NotificationService.notify_finder(q)
        if ok:
            response = build_response(session.session_id, state, "습득자에게 질문지를 전달했어요. 승인/답변을 기다려주세요.",
                      data={"questionnaire_id": str(q.id), "notification_sent": True})
        else:
            response = build_response(session.session_id, state, "알림 전송 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
                      data={"questionnaire_id": str(q.id), "notification_sent": False})
        return response

    if state == QuestionState.DONE:
        # 이미 완료된 세션
        response = build_response(session.session_id, state, "이미 질문을 모두 받았습니다. 새로 시작하려면 세션을 초기화하세요.")
        return response