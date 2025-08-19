from django.db import models

class PoliceFoundItem(models.Model):
    atcId = models.CharField(max_length=255, primary_key=True, help_text="관리ID")
    clrNm = models.CharField(max_length=100, blank=True, null=True, help_text="색상명")
    depPlace = models.CharField(max_length=255, blank=True, null=True, help_text="보관장소")
    fdFilePathImg = models.URLField(max_length=500, blank=True, null=True, help_text="습득물 이미지 경로")
    fdPrdtNm = models.CharField(max_length=255, blank=True, null=True, help_text="습득물명")
    fdSbjt = models.TextField(blank=True, null=True, help_text="내용")
    fdSn = models.IntegerField(blank=True, null=True, help_text="순번")
    fdYmd = models.DateField(blank=True, null=True, help_text="습득일")
    prdtClNm = models.CharField(max_length=255, blank=True, null=True, help_text="물품분류명")

    # 추가 필드 (데이터 동기화 시간 등)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "경찰청 습득물"
        verbose_name_plural = "경찰청 습득물 목록"
        ordering = ['-fdYmd', '-atcId'] # 최신 습득일, 관리ID 순으로 정렬

    def __str__(self):
        return f"{self.fdPrdtNm} ({self.atcId})"
