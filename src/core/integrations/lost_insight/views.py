from django.utils import timezone
from django.db.models import Count
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CategoryDailyCount

class LostInsightRecommendView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        today = timezone.now().date()
        
        # 오늘 날짜 기준 카테고리별 검색 횟수 집계
        top = (
            CategoryDailyCount.objects
            .filter(date=today)
            .values("category", "count")
            .order_by("-count")
            .first()
        )

        if not top:
            # 데이터가 없을 때의 안전한 응답
            data = {"recommend": None, "reason": "no_search_today"}
        else:
            data = {"recommend": top["category"], "count": top["count"]}

        return Response(
            {"status": "success", "code": 200, "data": data, "message": "조회 성공"},
            status=status.HTTP_200_OK,
        )
