from django.db import models
from config import settings

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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,            
        on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.JSONField(default=dict)
    color = models.CharField(max_length=50, default="unknown")
    found_at = models.DateTimeField()
    found_location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=7, null=True, blank=True)
    image_urls = models.JSONField(default=list, null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available'
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)