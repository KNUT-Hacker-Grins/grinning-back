from django.core.paginator import Paginator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.reports.models import Report
from apps.reports.serializers import ReportSerializer

class ReportListView(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsAdminUser]

    def get(self, request):
        status_param = request.query_params.get('status')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))

        reports = Report.objects.all().order_by('-created_at')
        if status_param:
            reports = reports.filter(status=status_param)

        paginator = Paginator(reports, limit)
        current_page = paginator.get_page(page)

        serializer = ReportSerializer(current_page, many=True)

        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "reports": serializer.data,
                "page": page,
                "total": paginator.count
            },
            "message": "조회 성공"
        }, status=200)