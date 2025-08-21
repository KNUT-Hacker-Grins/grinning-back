from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import AllowAny 
from .models import Report
from .serializers import ReportSerializer
from core.features.lostfound.lost_items.models import LostItem

class MarkAsFoundView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAdminUser]

    def patch(self, request, id):
        lost_item = get_object_or_404(LostItem, id=id)

        found_description = request.data.get('found_description')
        if not found_description:
            return Response({
                "status": "fail",
                "code": 400,
                "message": "found_description은 필수입니다."
            }, status=http_status.HTTP_400_BAD_REQUEST)

        lost_item.status = 'found'
        lost_item.found_description = found_description
        lost_item.save()

        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "id": lost_item.id,
                "status": lost_item.status
            },
            "message": "회수 완료 처리"
        }, status=http_status.HTTP_200_OK)
    
class ReportCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        serializer = ReportSerializer(data={**request.data, 'post_id': post_id}, context={'request': request})
        if serializer.is_valid():
            report = serializer.save()
            return Response({
                "status": "success",
                "code": 201,
                "data": {"report_id": report.id},
                "message": "신고 접수 완료"
            }, status=201)
        return Response({
            "status": "fail",
            "code": 400,
            "errors": serializer.errors,
            "message": "입력값이 유효하지 않습니다."
        }, status=400)
    
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