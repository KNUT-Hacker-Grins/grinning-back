from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated

from apps.lost_items.models import LostItem

class MarkAsFoundView(APIView):
    permission_classes = [IsAuthenticated]
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