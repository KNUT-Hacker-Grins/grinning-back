from django.db import models

class CategoryDailyCount(models.Model):
    CATEGORY_CHOICES = [
        ("jewelry", "보석_귀금속_시계"),
        ("electronics", "전자기기"),
        ("stationery", "문구류"),
        ("fashion", "피혁_잡화"),
        ("etc", "기타"),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()
    count = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ("category", "date")
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["category", "date"]),
        ]

    def __str__(self):
        return f"{self.date} {self.category}: {self.count}"
