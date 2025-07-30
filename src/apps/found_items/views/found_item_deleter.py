from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.found_items.models import FoundItem

class FoundItemDeleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, id):
        item = get_object_or_404(FoundItem, id=id)

        # 비인증 사용자이거나 게시글 작성자가 아닌 경우 권한 거부
        if not request.user.is_authenticated or item.user != request.user:
            raise PermissionDenied("본인 게시글만 삭제할 수 있습니다.")

        item.delete()
        return Response({
            "status": "success",
            "code": 200,
            "message": "삭제 완료"
        }, status=status.HTTP_200_OK)
