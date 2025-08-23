from django.db import models

class PoliceFoundItem(models.Model):
    atcId = models.CharField(max_length=255, primary_key=True, verbose_name="관리ID")
    depPlace = models.CharField(max_length=255, verbose_name="보관장소", default='', blank=True)
    fdFilePathImg = models.URLField(max_length=1024, verbose_name="습득물사진파일경로", default='', blank=True)
    fdPrdtNm = models.CharField(max_length=255, verbose_name="습득물품명", default='', blank=True)
    fdSn = models.CharField(max_length=255, verbose_name="습득순번", default='', blank=True)
    fdYmd = models.CharField(max_length=255, verbose_name="습득일자", default='', blank=True)
    prdtClNm = models.CharField(max_length=255, verbose_name="물품분류명", default='', blank=True)
    rnum = models.IntegerField(verbose_name="순번", default=0)
    clrNm = models.CharField(max_length=255, verbose_name="색상", default='', blank=True)
    tel = models.CharField(max_length=255, verbose_name="연락처", default='', blank=True)

    def __str__(self):
        return f"{self.fdPrdtNm} ({self.atcId})"


class PoliceLostItem(models.Model):
    atcId = models.CharField(max_length=255, primary_key=True, verbose_name="관리ID")
    lstPlace = models.CharField(max_length=255, verbose_name="분실장소", default='', blank=True)
    lstFilePathImg = models.URLField(max_length=1024, verbose_name="분실물사진파일경로", default='', blank=True)
    lstPrdtNm = models.CharField(max_length=255, verbose_name="분실물품명", default='', blank=True)
    lstSn = models.CharField(max_length=255, verbose_name="분실순번", default='', blank=True)
    lstYmd = models.CharField(max_length=255, verbose_name="분실일자", default='', blank=True)
    prdtClNm = models.CharField(max_length=255, verbose_name="물품분류명", default='', blank=True)
    rnum = models.IntegerField(verbose_name="순번", default=0)
    clrNm = models.CharField(max_length=255, verbose_name="색상", default='', blank=True)
    tel = models.CharField(max_length=255, verbose_name="연락처", default='', blank=True)
    lstSbjt = models.CharField(max_length=255, verbose_name="분실물제목", default='', blank=True)

    def __str__(self):
        return f"{self.lstPrdtNm} ({self.atcId})"
