from enum import Enum
from django.utils import timezone
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChatRequestSerializer
from .session import _ensure_session
from .chatbot_handler import ChatBotHandler


class ChatbotHealthView(APIView):
    def get(self, request):
        return Response({"ok": True, "time": timezone.now().isoformat()})


class ChatbotMessageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:    
            session = _ensure_session(data.get("session_id", ""))
            
            handler = ChatBotHandler(session, data.get("intent"), data.get("message"))
            reply_dict = handler.handle_request()  
            return Response(reply_dict, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response(
                {"error": "Internal Server Error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
