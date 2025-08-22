from django.db import models
from django.contrib.auth import get_user_model
from config import settings

User = get_user_model()

class ChatSession(models.Model):
    session_id = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,            
        on_delete=models.SET_NULL
    )
    state = models.CharField(max_length=64, default="idle")
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class InquiryLog(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='inquiries')
    message = models.TextField()
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
