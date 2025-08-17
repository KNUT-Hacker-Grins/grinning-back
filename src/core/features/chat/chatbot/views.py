from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import InquiryLog
from ml.nlp.similarity import LostItemsRecommander
from .serializers import ChatRequestSerializer
from .services.session import _ensure_session
from .domain.state import ChatState
from .domain.reply import ChatReply
from ml.llm.gemini_text2json import parse_item_by_genai 

class ChatbotHealthView(APIView):
    def get(self, request):
        return Response({"ok": True, "time": timezone.now().isoformat()})

class ChatbotMessageView(APIView):
    
    WELCOME_CHOICES = ["분실물 찾기", "분실물 신고", "기타 문의"]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session = _ensure_session(data.get("session_id", ""))
        intent = (data.get("intent") or "").strip()
        message = (data.get("message") or "").strip()

        # 상태 전환: 키워드 선택 처리
        if intent in self.WELCOME_CHOICES and session.state == ChatState.IDLE.value:
            if intent == "분실물 찾기":
                session.state = ChatState.AWAITING_DESCRIPTION.value
                session.context = {"intent": intent}
                session.save(update_fields=["state", "context", "updated_at"])
                
                return Response({
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": ChatReply.분실물찾기.value,
                    "choices": []
                })

            elif intent == "분실물 신고":
                session.context = {"intent": intent}
                session.save(update_fields=["context", "updated_at"])
                
                return Response({
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": ChatReply.분실물신고.value,
                    "choices": []
                })

            elif intent == "기타 문의":
                session.state = ChatState.OTHER.value
                session.context = {"intent": intent}
                session.save(update_fields=["state", "context", "updated_at"])
                
                return Response({
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": ChatReply.기타문의.value,
                    "choices": []
                })

        if session.state == ChatState.AWAITING_DESCRIPTION.value:
            if not message: 
                return Response({
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": ChatReply.특징입력대기.value,
                    "choices": []
                })

            InquiryLog.objects.create(session=session, message=message)
            query = parse_item_by_genai(message)
            recs = LostItemsRecommander(query, top_k=5)

            if recs:
                return Response({
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": ChatReply.유사분실물추천.value,
                    "choices": ["🔍 검색하기"],
                    "recommendations": recs
                })
            else:
                return Response({
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": ChatReply.유사분실물찾지못함.value,
                    "choices": ["🔍 검색하기"],
                    "recommendations": []
                })

        if session.state == ChatState.OTHER.value:
            if message:
                InquiryLog.objects.create(session=session, message=message, extra={"type":"etc"})
                return Response({
                    "session_id": session.session_id,
                    "state": session.state,
                    "reply": ChatReply.기타문의접수완료.value,
                    "choices": self.WELCOME_CHOICES
                })

            return Response({
                "session_id": session.session_id,
                "state": session.state,
                "reply": ChatReply.기타문의내용작성.value,
                "choices": []
            })
 
        return Response({
            "session_id": session.session_id,
            "state": session.state,
            "reply": ChatReply.안내내용.value,
            "choices": self.WELCOME_CHOICES
        })
