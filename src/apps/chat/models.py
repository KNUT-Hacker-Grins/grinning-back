from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    # 게시물 참조 정보 (found/lost 구분)
    post_type = models.CharField(max_length=10, choices=[('found', 'Found'), ('lost', 'Lost')])
    post_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ('post_type', 'post_id',)  # 중복 방지 키 아님 (별도 로직 필요)

    def __str__(self):
        return f"ChatRoom({self.id})"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=10, default='text')  # text, image, etc.
    timestamp = models.DateTimeField(auto_now_add=True)