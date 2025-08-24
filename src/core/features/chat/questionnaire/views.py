from django.db import transaction
from django.utils import timezone
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Questionnaire
from .serializers import DeliverRequestSerializer, ApproveRequestSerializer
from .services.chat import ChatService
from .services.service import handle_user_input
from .services.notification import NotificationService
from .utils import push_step
from core.features.chat.chat.models import ChatRoom
from core.features.chat.chatbot.session import get_or_create_session_from_request

class ChatbotMessageView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        # 세션 식별: 쿠키 우선, 없으면 body.session_id 허용
        session, _ = get_or_create_session_from_request(request)
        body = request.data or {}
        text = (body.get("text") or "").strip()
        post_id = body.get("post_id")  # 최초 1회 포함하면 세션.persist

        if not text:
            return Response({"ok": False, "error": "EMPTY_TEXT", "message": "text가 비어있습니다."}, status=400)

        # 사용자가 친 메시지를 즉시 화면에 보여주고 싶다면(옵션):
        from .utils import push_step
        push_step(session.session_id, "user", text)

        # 상태 머신 처리
        handle_user_input(session, text, maybe_post_id=post_id)

        # 프론트는 WebSocket으로 단계 메시지를 이미 받음. REST 응답은 상태만 간단히 반환
        return Response({
            "ok": True,
            "session_id": session.session_id,
            "state": session.state,
        })
    
class QuestionnaireDeliverAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        s = DeliverRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        session_id = s.validated_data["session_id"]
        post_id = s.validated_data["post_id"]

        # 1단계: 접수 메시지
        push_step(session_id, "bot", "질문지 전달 요청을 받았어요. 습득자에게 알리는 중...")

        post = ChatRoom.objects.select_for_update().get(id=post_id)

        q = Questionnaire.objects.create(
            session_id=session_id,
            post=post,
            status=Questionnaire.Status.PENDING,
            delivered_at=timezone.now(),
        )

        # 2단계: 알림 발송
        push_step(session_id, "system", "알림 전송을 준비 중입니다...")
        ok, _ = NotificationService.notify_finder(q)

        # 3단계: 발송 결과
        if ok:
            push_step(session_id, "bot", "습득자에게 질문지를 전달했어요. 답변/승인을 기다려주세요.")
        else:
            push_step(session_id, "bot", "알림 전송에 문제가 있어요. 잠시 후 다시 시도해주세요.")

        # 최종 REST 응답(동기)
        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "questionnaire_id": str(q.id),
                "message": "습득자에게 전달되었습니다",
                "notification_sent": bool(ok),
            },
            "message": "전달 완료"
        }, status=status.HTTP_200_OK)


class QuestionnaireApproveAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        s = ApproveRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        qid = s.validated_data["questionnaire_id"]
        action = s.validated_data["action"]
        reason = s.validated_data.get("reason")

        q = Questionnaire.objects.select_for_update().get(id=qid)
        session_id = q.session_id

        push_step(session_id, "system", f"승인 요청 수신: {action}")

        if action == "approve":
            q.status = Questionnaire.Status.APPROVED
            q.approved_at = timezone.now()
            q.reason = None
            q.save(update_fields=["status", "approved_at", "reason"])

            # 채팅방 생성
            push_step(session_id, "system", "채팅방을 생성하는 중...")
            room_id = ChatService.create_room_for_questionnaire(q)
            push_step(session_id, "bot", "승인 완료! 채팅방이 생성되었어요. 바로 대화해 보세요.", data={"room_id": room_id})

            return Response({
                "status": "success",
                "code": 200,
                "data": {
                    "action": "approve",
                    "auto_chat_created": True,
                    "room_id": room_id,
                    "message": "승인되어 채팅방이 생성되었습니다"
                }
            }, status=status.HTTP_200_OK)

        # reject
        q.status = Questionnaire.Status.REJECTED
        q.rejected_at = timezone.now()
        q.reason = reason
        q.save(update_fields=["status", "rejected_at", "reason"])

        push_step(session_id, "bot", f"질문지가 거부되었어요. 사유: {reason} 다시 시도해볼까요?", data={"retry_allowed": True})

        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "action": "reject",
                "reason": reason,
                "retry_allowed": True,
                "message": "질문지가 거부되었습니다"
            }
        }, status=status.HTTP_200_OK)
