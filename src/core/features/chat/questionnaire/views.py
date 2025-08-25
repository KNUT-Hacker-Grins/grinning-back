from django.db import transaction
from django.utils import timezone
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Questionnaire
from .serializers import DeliverRequestSerializer, ApproveRequestSerializer
from .notification import NotificationService
from .service import handle_user_input
from .session import get_or_create_session_from_request, COOKIE_NAME
from core.features.chat.chat.models import ChatRoom

class QuestionHealthView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # 익명 허용 시

    def get(self, request):
        session, created = get_or_create_session_from_request(request)
        
        session.state = "INIT"
        session.save(update_fields=["state"])

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
    
class QuestionMessageView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    # post 메서드를 비동기(async)에서 동기(def)로 변경합니다.
    def post(self, request):
        # 세션 식별: 쿠키 우선, 없으면 body.session_id 허용
        session, _ = get_or_create_session_from_request(request)
        body = request.data or {}
        text = (body.get("text") or "").strip()
        post_id = body.get("post_id")  # 최초 1회 포함하면 세션.persist

        try:    
            response = handle_user_input(session, text, post_id)
            return Response(response, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response(
                {"error": "Internal Server Error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QuestionnaireDeliverAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        s = DeliverRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        session_id = s.validated_data["session_id"]
        post_id = s.validated_data["post_id"]

        try:
            with transaction.atomic():
                # ORM 쿼리는 기본적으로 동기이므로 직접 호출합니다.
                post = ChatRoom.objects.select_for_update().get(id=post_id)

                q = Questionnaire.objects.create(
                    session_id=session_id,
                    post=post,
                    status=Questionnaire.Status.PENDING,
                    delivered_at=timezone.now(),
                )

                # NotificationService.notify_finder가 동기 함수이므로 직접 호출합니다.
                ok, _ = NotificationService.notify_finder(q)

                if ok:
                    message = "습득자에게 질문지를 전달했어요. 답변/승인을 기다려주세요."
                else:
                    message = "알림 전송에 문제가 있어요. 잠시 후 다시 시도해주세요."
                
                return Response({
                    "status": "success",
                    "code": 200,
                    "data": {
                        "questionnaire_id": str(q.id),
                        "message": message,  # 메시지를 응답에 포함
                        "notification_sent": bool(ok),
                    },
                    "message": "전달 완료"
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuestionnaireApproveAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        s = ApproveRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        qid = s.validated_data["questionnaire_id"]
        action = s.validated_data["action"]
        reason = s.validated_data.get("reason")

        try:
            with transaction.atomic():
                q = Questionnaire.objects.select_for_update().get(id=qid)
                
                if action == "approve":
                    q.status = Questionnaire.Status.APPROVED
                    q.approved_at = timezone.now()
                    q.reason = None
                    q.save(update_fields=["status", "approved_at", "reason"])

                    message = "승인 완료! 채팅방이 생성되었어요. 바로 대화해 보세요."

                    return Response({
                        "status": "success",
                        "code": 200,
                        "data": {
                            "action": "approve",
                            "auto_chat_created": True,
                            "room_id": q.post_id,
                            "message": message
                        },
                        "message": "승인 완료"
                    }, status=status.HTTP_200_OK)
                else:  # reject
                    q.status = Questionnaire.Status.REJECTED
                    q.rejected_at = timezone.now()
                    q.reason = reason
                    q.save(update_fields=["status", "rejected_at", "reason"])

                    message = f"질문지가 거부되었어요. 사유: {reason} 다시 시도해볼까요?"

                    return Response({
                        "status": "success",
                        "code": 200,
                        "data": {
                            "action": "reject",
                            "reason": reason,
                            "retry_allowed": True,
                            "message": message
                        },
                        "message": "거부 완료"
                    }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)