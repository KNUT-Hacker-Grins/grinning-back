from django.db import models

class PoliceFoundItem(models.Model):
    atcId = models.CharField(max_length=255, primary_key=True, verbose_name="관리ID")
    depPlace = models.CharField(max_length=255, verbose_name="보관장소")
    fdFilePathImg = models.URLField(max_length=1024, verbose_name="습득물사진파일경로")
    fdPrdtNm = models.CharField(max_length=255, verbose_name="습득물품명")
    fdSn = models.CharField(max_length=255, verbose_name="습득순번")
    fdYmd = models.CharField(max_length=255, verbose_name="습득일자")
    prdtClNm = models.CharField(max_length=255, verbose_name="물품분류명")
    rnum = models.IntegerField(verbose_name="순번", default=0)
    clrNm = models.CharField(max_length=255, verbose_name="색상")
    tel = models.CharField(max_length=255, verbose_name="연락처")

    def __str__(self):
        return f"{self.fdPrdtNm} ({self.atcId})"


class PoliceLostItem(models.Model):
    atcId = models.CharField(max_length=255, primary_key=True, verbose_name="관리ID")
    lstPlace = models.CharField(max_length=255, verbose_name="분실장소")
    lstFilePathImg = models.URLField(max_length=1024, verbose_name="분실물사진파일경로")
    lstPrdtNm = models.CharField(max_length=255, verbose_name="분실물품명")
    lstSn = models.CharField(max_length=255, verbose_name="분실순번")
    lstYmd = models.CharField(max_length=255, verbose_name="분실일자")
    prdtClNm = models.CharField(max_length=255, verbose_name="물품분류명")
    rnum = models.IntegerField(verbose_name="순번", default=0)
    clrNm = models.CharField(max_length=255, verbose_name="색상")
    tel = models.CharField(max_length=255, verbose_name="연락처")
    lstSbjt = models.CharField(max_length=255, verbose_name="분실물제목")

    def __str__(self):
        return f"{self.lstPrdtNm} ({self.atcId})"
