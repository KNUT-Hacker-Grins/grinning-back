from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.found_items.serializers import FoundItemSerializer
from apps.found_items.utils import get_filtered_found_items


class AdminFoundItemListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        items, total, page, limit = get_filtered_found_items(request)
        serializer = FoundItemSerializer(items, many=True)
        return Response({
            "status": "success",
            "code": 200,
            "data": {
                "items": serializer.data,
                "page": page,
                "limit": limit,
                "total": total
            },
            "message": "관리자 조회 성공"
        }, status=status.HTTP_200_OK)
    