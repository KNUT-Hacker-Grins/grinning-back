from enum import Enum
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import InquiryLog
from .serializers import ChatRequestSerializer
from .services.session import _ensure_session
from .state import ChatState
from ml.llm.gemini import GeminiService  
from ml.nlp.similarity import LostItemsRecommander

class ChatbotHealthView(APIView):
    def get(self, request):
        return Response({"ok": True, "time": timezone.now().isoformat()})

WELCOME_CHOICES = ["분실물 찾기", "분실물 신고", "기타 문의"]
    
class ChatState:
    """
    IDLE: 아무 동작도 하지 않고 대기하는 상태
    AWAITING_DESCRIPTION: 유저가 물건(또는 사건 등)에 대한 설명을 입력하기를 기다리는 상태
    OTHER : 정의된 정상 플로우(IDLE, AWAITING_DESCRIPTION 등) 이외의 상태
    """
    IDLE = "idle" 
    AWAITING_DESCRIPTION = "awaiting_description" 
    OTHER = "other"

class ChatReply:
    안내내용 = "무엇을 도와드릴까요?"
    분실물찾기 = "어떤 물건을 잃어버리셨나요? 색상/형태/브랜드 등 자세히 적어주세요."
    분실물신고 = "신고 게시글 작성 페이지로 이동합니다. (예: /report/new)"
    기타문의 = "문의 내용을 자유롭게 작성해 주세요. 관리자가 확인 후 답변드립니다." 
    특징입력대기 = "물건의 상세 설명을 입력해 주세요. 예) '검정색 접이식 우산'"
    유사분실물추천 = "다음 항목이 비슷해 보여요. 맞는 것이 없다면 '🔍 검색하기'를 눌러 상세 검색으로 이동할 수 있어요." 
    유사분실물찾지못함 = "유사한 항목을 찾지 못했어요. '🔍 검색하기'를 눌러 직접 검색해 보시겠어요?" 
    기타문의내용작성 = "문의 내용을 작성해 주세요."
    기타문의접수완료 = "문의가 접수되었습니다. 빠르게 확인하겠습니다. 또 도와드릴까요?"
    

def handle_idle_state(session, intent=None, message=None):
    if intent == "분실물 찾기":
        session.state = ChatState.AWAITING_DESCRIPTION
        session.context = {"intent": intent}
        session.save(update_fields=["state", "context", "updated_at"])
        return ChatReply.분실물찾기, []
        
    elif intent == "분실물 신고":
        session.context = {"intent": intent}
        session.save(update_fields=["context", "updated_at"])
        
        return ChatReply.분실물신고, []

    elif intent == "기타 문의":
        session.state = ChatState.OTHER
        session.context = {"intent": intent}
        session.save(update_fields=["state", "context", "updated_at"])
        
        return ChatReply.기타문의, []

def handle_awaiting_description_state(session, intent=None, message=None):
    if not message: 
        return ChatReply.특징입력대기, []
    
    InquiryLog.objects.create(session=session, message=message)
    query = GeminiService.call_gemini_for_parsing_text(message)
    recs = LostItemsRecommander(query, top_k=5)

    if recs:
        return ChatReply.유사분실물추천, ["🔍 검색하기"], recs
    else:   
        return ChatReply.유사분실물찾지못함, ["🔍 검색하기"]
        
def handle_other_state(session, intent=None, message=None):
    if message:
        InquiryLog.objects.create(session=session, message=message, extra={"type":"etc"})
        return ChatReply.기타문의접수완료, WELCOME_CHOICES

    return ChatReply.기타문의내용작성, []
    
class ChatbotMessageView(APIView):
    
    STATE_HANDLERS = {
        ChatState.IDLE: handle_idle_state,
        ChatState.AWAITING_DESCRIPTION: handle_awaiting_description_state,
        ChatState.OTHER: handle_other_state
    }

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session = _ensure_session(data.get("session_id", ""))
        handler = self.STATE_HANDLERS.get(session.state)
    
        if handler:
            reply, choices, *recs = handler(session, data.get("intent"), data.get("message"))
            return self._send_response(session, reply, choices, recs if recs else [])
        
        return self._send_response(session.session_id, session.state, ChatReply.안내내용, WELCOME_CHOICES, [])

    def _send_response(self, session, reply, choices=[], recommendations=[]):
        return Response({
            "session_id": session.session_id,
            "state": session.state,
            "reply": reply,
            "choices": choices,
            "recommendations": recommendations
        })