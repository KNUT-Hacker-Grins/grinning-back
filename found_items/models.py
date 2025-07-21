from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.conf import settings

class LostItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 등록한 유저
    title = models.CharField(max_length=100)
    description = models.TextField()
    found_at = models.DateTimeField()
    location = models.CharField(max_length=200)
    image_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
