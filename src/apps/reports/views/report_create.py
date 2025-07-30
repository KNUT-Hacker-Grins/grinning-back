from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.reports.serializers import ReportSerializer

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