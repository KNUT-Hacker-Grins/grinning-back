from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.found_items.serializers import FoundItemSerializer


class FoundItemCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = FoundItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 비인증 사용자의 경우 None을 저장
        user = request.user if request.user.is_authenticated else None
        serializer.save(user=user)

        return Response({
            "status": "success",
            "code": 201,
            "data": serializer.data,
            "message": "등록 완료"
        }, status=status.HTTP_201_CREATED)

