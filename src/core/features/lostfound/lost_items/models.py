import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class LostItem(models.Model):
    """잃어버린 물건 신고 모델"""
    STATUS_CHOICES = [
            ('searching', '찾는 중'),
            ('found', '찾음'),
            ('cancelled', '취소')
        ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )  # 신고한 사용자

    title = models.CharField(max_length=100)  # 분실물 제목
    description = models.TextField()  # 상세 설명
    category = models.JSONField(default=list)
    color = models.CharField(max_length=30)
    lost_at = models.DateTimeField()  # 분실한 날짜/시간
    lost_location = models.CharField(max_length=200)  # 분실한 장소
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=7, null=True, blank=True)
    image_urls = models.JSONField(default=list)  # 이미지 URL 배열
    reward = models.DecimalField(max_digits=10, decimal_places=0, default=0, validators=[MinValueValidator(0)]) # 현상금 (음수 방지)  
    status = models.CharField(
        max_length=20,
        default='searching',
        choices=STATUS_CHOICES
    )  # 상태
    created_at = models.DateTimeField(auto_now_add=True)  # 등록일시
    updated_at = models.DateTimeField(auto_now=True)  # 수정일시

    class Meta:
        ordering = ['-created_at']  # 최신순 정렬

    def __str__(self):
        user_name = self.user.name if self.user and hasattr(self.user, 'name') else "Unknown User"
        return f"{self.title} - {user_name}"
    
class CategoryCount(models.Model):
    CATEGORY_CHOICES = [
        ("jewelry", "보석_귀금속_시계"),
        ("electronics", "전자기기"),
        ("stationery", "문구류"),
        ("fashion", "피혁_잡화"),
        ("etc", "기타"),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    search_count = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.category}: {self.category_count}"