from enum import Enum
from django.utils import timezone
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChatRequestSerializer
from .session import get_or_create_session_from_request, COOKIE_NAME, _ensure_session_by_id
from .chatbot_handler import ChatBotHandler

class ChatbotHealthView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # 익명 허용 시

    def get(self, request):
        session, created = get_or_create_session_from_request(request)
        resp = Response({
            "ok": True,
            "time": timezone.now().isoformat(),
            "state": session.state,
            "session_id": session.session_id,
            "created": created,
        })
        
        # 클라이언트가 다음 요청에 자동으로 session_id를 보내도록 쿠키로 고정
        resp.set_cookie(
            key=COOKIE_NAME,
            value=session.session_id,
            max_age=60 * 60 * 24 * 7,  # 7일
            httponly=True,
            samesite="Lax",            # SPA가 동일 사이트면 Lax로 충분. 크로스 도메인이면 'None' + Secure
            secure=False,              # https면 True
        )
        return resp

class ChatbotMessageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:    
            session, _ = get_or_create_session_from_request(request)
            
            handler = ChatBotHandler(session, data.get("intent"), data.get("message"))
            reply_dict = handler.handle_request()  
            return Response(reply_dict, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response(
                {"error": "Internal Server Error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
