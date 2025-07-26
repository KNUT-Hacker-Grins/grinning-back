from django.db import models
from django.conf import settings

"""
available	주인을 기다리고 있음 (기본 상태)
returned	실제로 물건을 해당 주인에게 돌려줌. 처리 완료 상태
archived	오래돼서 숨긴 상태, 보관종료 등 (선택사항)
"""

class FoundItem(models.Model):
    STATUS_CHOICES = [
        ('available', '보관 중'),      # 기본값
        ('returned', '수령 완료'),
        ('archived', '숨김 처리')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 등록한 유저
    title = models.CharField(max_length=100)
    description = models.TextField()
    found_at = models.DateTimeField()
    found_location = models.CharField(max_length=200)
    image_url = models.URLField(max_length=500)
    category = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available'
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)