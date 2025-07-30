from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.found_items.models import FoundItem
from apps.found_items.serializers import FoundItemSerializer

class FoundItemUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request, id):
        item = get_object_or_404(FoundItem, id=id)

        # 비인증 사용자이거나 게시글 작성자가 아닌 경우 권한 거부
        if not request.user.is_authenticated or item.user != request.user:
            raise PermissionDenied("본인 게시글만 수정할 수 있습니다.")

        serializer = FoundItemSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "수정 완료"
        }, status=status.HTTP_200_OK)


