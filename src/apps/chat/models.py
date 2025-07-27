from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)

    # 게시물 참조 정보 (found/lost 구분)
    post_type = models.CharField(
        max_length=10,
        choices=[('found', 'Found'), ('lost', 'Lost')]
    )
    post_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ('post_type', 'post_id')  # 중복 방지 논리 키 (DB 유니크는 아님)

    def __str__(self):
        return f"ChatRoom({self.id})"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=10, default='text')  # 'text', 'image', 등
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)