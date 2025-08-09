from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.found_items.models import FoundItem
from apps.found_items.serializers import FoundItemDetailSerializer

class FoundItemDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        item = get_object_or_404(FoundItem, id=id)
        serializer = FoundItemDetailSerializer(item)
        return Response({
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "조회 성공"
        }, status=status.HTTP_200_OK)
