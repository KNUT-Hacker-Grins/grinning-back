import uuid
from rest_framework.response import Response
from .models import InquiryLog, ChatSession
from ml.llm.gemini import GeminiService  
from ml.nlp.similarity import LostItemsRecommander


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
    
WELCOME_CHOICES = ["분실물 찾기", "분실물 신고", "기타 문의"]
SEARCH_CHOICE = ["🔍 검색하기"]

class ChatBotHandler:
    
    STATE_HANDLERS = {
        ChatState.IDLE: "_handle_idle_state",
        ChatState.AWAITING_DESCRIPTION: "_handle_awaiting_description_state",
        ChatState.OTHER: "_handle_other_state",
    }

    def __init__(self, session, intent, message):
        self.session = session
        self.intent = intent
        self.message = message
        self.response = {}

    def handle_request(self):
        """
        현재 세션 상태에 따라 적절한 핸들러를 호출하여 응답을 생성합니다.
        Dispatches to the correct handler based on the current session state to generate a response.
        """
        current_state = self.session.state
        handler_method_name = self.STATE_HANDLERS.get(current_state)
        
        if handler_method_name:
            handler = getattr(self, handler_method_name)
            handler()
        else:
            # 정의되지 않은 상태에 대한 예외 처리
            # Fallback for undefined states
            self.response = self._send_response(
                reply=ChatReply.안내내용,
                choices=WELCOME_CHOICES
            )
        
        # 최종 응답에 세션 및 상태 정보를 추가합니다.
        # Add session and state information to the final response.
        self.response["session_id"] = self.session.session_id
        self.response["state"] = self.session.state
        
        return self.response

    def _handle_idle_state(self):
        if self.intent == "분실물 찾기":
            self.session.state = ChatState.AWAITING_DESCRIPTION
            self.session.context = {"intent": self.intent}
            self.session.save(update_fields=["state", "context", "updated_at"])
            self.response = self._send_response(ChatReply.분실물찾기)
            
        elif self.intent == "분실물 신고":
            self.session.context = {"intent": self.intent}
            self.session.save(update_fields=["context", "updated_at"])
            self.response = self._send_response(ChatReply.분실물신고)

        elif self.intent == "기타 문의":
            self.session.state = ChatState.OTHER
            self.session.context = {"intent": self.intent}
            self.session.save(update_fields=["state", "context", "updated_at"])
            self.response = self._send_response(ChatReply.기타문의)
        else:
            self.response = self._send_response(
                reply=ChatReply.WELCOME,
                choices=WELCOME_CHOICES
            )

    def _handle_awaiting_description_state(self):
        if not self.message: 
            self.response = self._send_response(ChatReply.특징입력대기)
            return 
        
        InquiryLog.objects.create(session=self.session, message=self.message)

        try:
            query = GeminiService.call_gemini_for_parsing_text(self.message)
            recs = LostItemsRecommander(query, top_k=5)

            if recs:
                self.response = self._send_response(ChatReply.유사분실물추천, SEARCH_CHOICE, recs)
            else:   
                self.response =  self._send_response(ChatReply.유사분실물찾지못함, SEARCH_CHOICE)
            
        except Exception as e:
            # Gemini 또는 Recommender 서비스에서 오류 발생 시 처리
            # Handle errors from Gemini or Recommender services.
            print(f"Error in awaiting description state: {e}")
            self.response = self._create_response(
                reply=ChatReply.ERROR_OCCURRED,
                choices=WELCOME_CHOICES
            )
            # 오류 발생 시 상태를 초기화하여 무한 루프를 방지합니다.
            # Reset state on error to prevent an infinite loop.
            self.session.state = ChatState.IDLE
            self.session.save(update_fields=["state", "updated_at"])
            
    def _handle_other_state(self):
        if self.message:
            InquiryLog.objects.create(session=self.session, message=self.message, extra={"type":"etc"})
            self.response = self._send_response(ChatReply.기타문의접수완료, WELCOME_CHOICES, [])
            self.session.state = ChatState.IDLE
            self.session.save(update_fields=["state", "updated_at"])
        else:
            self.response = self._send_response(ChatReply.기타문의내용작성)

    def _send_response(self, reply, choices=[], recommendations=[]):
        return Response({
            "session_id": self.session.session_id,
            "state": self.self.session.state,
            "reply": reply,
            "choices": choices,
            "recommendations": recommendations
        })