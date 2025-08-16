import uuid
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatRequestSerializer, ChatResponseSerializer
from .models import ChatSession, InquiryLog
from .state import ChatState
from .nlp import extract_structured
from .similarity import recommend_by_tfidf

WELCOME_CHOICES = ["분실물 찾기", "분실물 신고", "기타 문의"]

def _ensure_session(session_id: str = "") -> ChatSession:
    if not session_id:
        session_id = uuid.uuid4().hex[:16]
        return ChatSession.objects.create(session_id=session_id, state=ChatState.IDLE.value)
    try:
        return ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return ChatSession.objects.create(session_id=session_id, state=ChatState.IDLE.value)

class ChatbotHealthView(APIView):
    def get(self, request):
        return Response({"ok": True, "time": timezone.now().isoformat()})

class ChatbotMessageView(APIView):
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session = _ensure_session(data.get("session_id", ""))
        intent = (data.get("intent") or "").strip()
        message = (data.get("message") or "").strip()

        # 상태 전환: 키워드 선택 처리
        if intent in WELCOME_CHOICES and session.state == ChatState.IDLE.value:
            if intent == "분실물 찾기":
                session.state = ChatState.AWAITING_DESCRIPTION.value
                session.context = {"intent": intent}
                session.save(update_fields=["state", "context", "updated_at"])
                reply = "어떤 물건을 잃어버리셨나요? 색상/형태/브랜드 등 자세히 적어주세요."
                res = {
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": reply,
                    "choices": []
                }
                return Response(res)

            elif intent == "분실물 신고":
                session.context = {"intent": intent}
                session.save(update_fields=["context", "updated_at"])
                reply = "신고 게시글 작성 페이지로 이동합니다. (예: /report/new)"
                res = {
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": reply,
                    "choices": []
                }
                return Response(res)

            elif intent == "기타 문의":
                session.state = ChatState.OTHER.value
                session.context = {"intent": intent}
                session.save(update_fields=["state", "context", "updated_at"])
                reply = "문의 내용을 자유롭게 작성해 주세요. 관리자가 확인 후 답변드립니다."
                res = {
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": reply,
                    "choices": []
                }
                return Response(res)

        # 상태별 처리
        if session.state == ChatState.AWAITING_DESCRIPTION.value:
            if not message:
                res = {
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": "물건의 상세 설명을 입력해 주세요. 예) '검정색 접이식 우산'",
                    "choices": []
                }
                return Response(res)

            InquiryLog.objects.create(session=session, message=message)
            meta = extract_structured(message)
            # 쿼리 문자열 생성 (간단히 category/color를 앞에 붙여 성능 보정)
            q = " ".join([meta.get("category",""), meta.get("color",""), meta.get("raw","")]).strip()
            recs = recommend_by_tfidf(q, top_k=5)

            if recs:
                reply = "다음 항목이 비슷해 보여요. 맞는 것이 없다면 '🔍 검색하기'를 눌러 상세 검색으로 이동할 수 있어요."
                res = {
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": reply,
                    "choices": ["🔍 검색하기"],
                    "recommendations": recs
                }
                return Response(res)
            else:
                reply = "유사한 항목을 찾지 못했어요. '🔍 검색하기'를 눌러 직접 검색해 보시겠어요?"
                res = {
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": reply,
                    "choices": ["🔍 검색하기"],
                    "recommendations": []
                }
                return Response(res)

        if session.state == ChatState.OTHER.value:
            if message:
                InquiryLog.objects.create(session=session, message=message, extra={"type":"etc"})
                reply = "문의가 접수되었습니다. 빠르게 확인하겠습니다. 또 도와드릴까요?"
                res = {
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": reply,
                    "choices": WELCOME_CHOICES
                }
                return Response(res)

            res = {
                "session_id": session.session_id,
                "state": session.state,
                "reply": "문의 내용을 작성해 주세요.",
                "choices": []
            }
            return Response(res)

        # 기본(웰컴)
        res = {
            "session_id": session.session_id,
            "state": session.state,
            "reply": "무엇을 도와드릴까요?",
            "choices": WELCOME_CHOICES
        }
        return Response(res)
