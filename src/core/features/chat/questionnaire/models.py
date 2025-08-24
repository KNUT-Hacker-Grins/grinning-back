import uuid
from django.db import models
from django.utils import timezone
from core.features.chat.chat.models import ChatRoom

class ChatState(models.TextChoices):
    INIT = "INIT"
    ASK_DESC = "ASK_DESC"      # 무엇을 잃어버렸나요?
    ASK_PLACE = "ASK_PLACE"    # 어디서 잃어버렸나요?
    ASK_TIME = "ASK_TIME"      # 언제 잃어버렸나요?
    DONE = "DONE"

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 프론트가 쓰는 세션 식별자(쿠키/URL로 사용). 사람이 읽기 좋은 별도 토큰을 두고 싶으면 추가
    session_id = models.CharField(max_length=64, unique=True, db_index=True)

    state = models.CharField(max_length=16, choices=ChatState.choices, default=ChatState.INIT)

    # 사용자 응답 누적
    lost_desc = models.TextField(null=True, blank=True)   # 무엇
    lost_place = models.TextField(null=True, blank=True)  # 어디
    lost_time = models.TextField(null=True, blank=True)   # 언제

    # 어떤 습득글(post)에 전달할지(최초 요청에서 받아 저장)
    post_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
class Questionnaire(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "PENDING"
        APPROVED = "APPROVED", "APPROVED"
        REJECTED = "REJECTED", "REJECTED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=64, db_index=True)
    post = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="questionnaires")

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField(null=True, blank=True)

    delivered_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} ({self.status})"


class NotificationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name="notifications")
    sent = models.BooleanField(default=False)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
